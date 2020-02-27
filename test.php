<?php

declare(strict_types=1);

// 	GLOBÁLNE PREMENNÉ //
$directory = getcwd();						//získanie default cesty k testom -t.j. aktuálny priečinok
$int_file = $directory . "/interpret.py";	//získanie default cesty k interpret.py
$parse_file = $directory . "/parse.php";	//získanie default cesty k parse.php
$jexamxml_file = "/pub/courses/ipp/jexamxml/jexamxml.jar";	//získanie default cesty k jexamxml.jar

$recursive_flag = false;	//bool pre prepínače
$parse_only_flag = false;
$int_only_flag = false;

$test_count = 0;			//counter na pocty testov 
$success = 0;				//uspesne testy
$failure = 0;				//neuspesne testy

//header pre tabulku do ktorej sa ukladaju vysledky testov 
$HTML = "<TABLE style='width: 100%;border:line;border-collapse: collapse;'>
    <tbody><tr style='background-color:#666666;color:white;border-collapse: collapse'>
    <th>Číslo</th><th>Názov</th><th>Úspešnosť</th><th>Predpokladaná návratová hodnota </th> <th> Návratová hodnota referenčného testu</th></tr>";

// Funkcia na overenie správnej formy XML
// pouzita funkcia zo zdroju http://h4cc.de/php-check-if-xml-is-valid-with-simplexmlelement.html
function isXmlStructureValid($file) {
    $prev = libxml_use_internal_errors(true);
    $return = true;
    try 
    {
      new SimpleXMLElement($file, 0, true);
    } 
    catch(Exception $e) 
    {
      $return = false;
    }
    if(count(libxml_get_errors()) > 0) 
    {
      $return = false;      // nastali chyby v xml takze to nie je spravne xml
    }
    //upratanie
    libxml_clear_errors();
    libxml_use_internal_errors($prev);
    return $return;
  }

function HTMLgen($filename, $exp_rc, $test_rc, $result, $test_count)
{
	global $HTML;
	$table_line;

	if($result == true)
	{
		$table_line = "<tr style='color:green;background-color:#ccffcc'>";
	}
	else
	{
		$table_line = "<tr style='color:red;background-color:#ffcccc'>";
	}

	$table_line = $table_line."<td>".$test_count."<td><i>".$filename."</i></td>";

	if($result == false)
	{
		$table_line = $table_line."<td>FAIL</td>";
		$table_line .= "<td>".$exp_rc."</td>"."<td>".$test_rc."</td>";
	}
	else
	{
		$table_line .= "</td><td>OK</td>";
		$table_line .= "<td>".$exp_rc."</td>"."<td>".$test_rc."</td>";
	}

	$table_line .= "</tr>";
	//echo $table_line;
	$HTML .= $table_line."\n";
		
}


function TestFiles($source)
{
	global $int_file, $parse_file, $jexamxml_file, $parse_only_flag, $parseArg, $interpArg;
	global $success, $failure, $test_count;

	if(substr($source, -2) == ".." || substr($source, -1) == ".")
	{
		return false;
	}
	if(substr($source, -4) == ".src")
	{
		$filename = substr($source, 0,-4);
		$ref_output = str_replace(".src",".out",$source);
		$ref_rc = str_replace(".src",".rc",$source);
		//$ref_in = str_replace(".src",".in",$source);	//zatial nema vyznam ked nemam interpret.py

		if(!file_exists($ref_output))
		{
			fwrite(STDERR, $test_count +1 . ".test - Referenčný output sa nenachádza v priečinku! Test sa nevykoná.\n");
			return false;
		}
		
		if(isXmlStructureValid($source) and $parse_only_flag == true)	//zistuje ci .src je xml subor
		{
			return false;
		}

		if(!file_exists($ref_rc))
		{
			$test_file = fopen($ref_rc, "w");
			if ($test_file == false)
			{
				fwrite(STDERR, "Výstupný súbor nejde otvoriť alebo neexituje!\n");
				ErrorExit(11);
			}
			fwrite($test_file,'0');
			fclose($test_file);
		}

		$test_file = fopen($ref_rc, "r");
		if ($test_file == false)
		{
			fwrite(STDERR, "Súbor .rc nie je možné načítať!\n");
			ErrorExit(11);
		}

		$exp_rc = fread($test_file,2);
		$exp_rc = intval($exp_rc);
		fclose($test_file);

		$test_count++;
		exec("php7.4 ".$parse_file ." <$source >temp_output", $result,$rc_out);
		if($rc_out != $exp_rc)
		{
			HTMLgen($filename,$exp_rc,$rc_out,false,$test_count);		//rc sa nerovnali
			$failure++;
		}
		else 
		{

			exec("java -jar ".$jexamxml_file." temp_output ".$ref_output, $result, $diff_ret); 
			if($diff_ret != 0 and $rc_out != $exp_rc)
		 	{
		 		$failure++;
				HTMLgen($filename,$exp_rc,$rc_out,false,$test_count);
			}
			else
			{
				$success++;
				HTMLgen($filename,$exp_rc,$rc_out,true,$test_count);
			}
		}
		unlink("temp_output");
	} 
	return True;	
}



/****************************************
*				  MAIN 	 				*
****************************************/
// ak nebol zadaný nijaký prepínač, t.j. vsetko zostane default
if($argc == 1)
{
	;//nejaka funkcia
}
else
{
    $long_params = array(
        "help",
        "directory:",
        "recursive",
        "parse-script:",
        "int-script:",
        "parse-only",
        "int-only",
        "jexamxml:"
    );

	$params = getopt ( "", $long_params);		//zíkanie argumentov a ich parsovanie do $params

	if (array_key_exists('help', $params) )
	{
		if($argc == 2) 							// zadany argument --help
		{
            echo <<<EOL
-Skript (test.php v jazyce PHP 7.4) slúži pre automatické testovanie 
postupnej aplikácie parse.php a interpret.py
--help viz společný parametr všech skriptů v sekci 2.2;
• --directory=path testy bude hledat v zadaném adresáři (chybí-li tento parametr, tak skript
prochází aktuální adresář; v případě zadání neexistujícího adresáře dojde k chybě 11);
• --recursive testy bude hledat nejen v zadaném adresáři, ale i rekurzivně ve všech jeho
podadresářích;
• --parse-script=file soubor se skriptem v PHP 7.4 pro analýzu zdrojového kódu v IPPcode20 (chybí-li tento parametr, tak implicitní hodnotou je parse.php uložený v aktuálním
adresáři);
• --int-script=file soubor se skriptem v Python 3.8 pro interpret XML reprezentace kódu
v IPPcode20 (chybí-li tento parametr, tak implicitní hodnotou je interpret.py uložený v aktuálním adresáři);
• --parse-only bude testován pouze skript pro analýzu zdrojového kódu v IPPcode20 (tento
parametr se nesmí kombinovat s parametry --int-only a --int-script), výstup s referenčním
výstupem (soubor s příponou out) porovnávejte nástrojem A7Soft JExamXML;
• --int-only bude testován pouze skript pro interpret XML reprezentace kódu v IPPcode20
(tento parametr se nesmí kombinovat s parametry --parse-only a --parse-script). Vstupní
program reprezentován pomocí XML bude v souboru s příponou src.
• --jexamxml=file soubor s JAR balíčkem s nástrojem A7Soft JExamXML. Je-li parametr
vynechán uvažuje se implicitní umístění /pub/courses/ipp/jexamxml/jexamxml.jar na serveru Merlin, kde bude test.php hodnocen.

EOL;
            exit(0);
        } 
        else 
        {
        	fwrite(STDERR, "Použi samostatne prepínač '--help' pre zobrazenie nápovedy.\n");
            exit(10);
        }
	}
	else
	{	$count_args = 1;	//lebo vzdy mam aspon jeden arg
		foreach ($params as $arg => $option) 
		{ 
			$count_args++;
			if ($arg == 'directory')							
			{
				global $directory;
				$tmp_directory = realpath($option);
				if ($tmp_directory == false)
				{	
					fwrite(STDERR, "Chyba! Zadaná neplatná adresa v --directory.\n");
					exit(11);
				}
								
				$directory = $tmp_directory;	
			}
			elseif ($arg == 'recursive')
			{
				global $recursive_flag;
				$recursive_flag = true;
			}
			elseif ($arg =='parse-script')
			{
				global $parse_file;
				if (is_file($option) == false)
				{
					exit(11);
				}
				$parse_file = $option;
			}
			elseif ($arg =='int-script')
			{
				global $int_file;
				if (is_file($option) == false)
				{
					exit(11);
				}
				$int_file = $option;
			}
			elseif ($arg =='parse-only')
			{
				global $parse_only_flag;
				$parse_only_flag = true;
			}
			elseif ($arg =='int-only')
			{
				global $int_only_flag;
				$int_only_flag = true;
			}
			elseif ($arg =='jexamxml')
			{
				global $jexamxml_file;
				if (is_file($option) == false)
				{
					exit(11);
				}
				$jexamxml_file = $option;
			}
			else
			{
				fwrite(STDERR, "Použi prepínač '--help' pre zobrazenie nápovedy.\n");
		        exit(10);
			}

			if (array_key_exists('parse-only', $params) and array_key_exists('int-only', $params))
			{
				fwrite(STDERR, "Chyba! Kombinovanie argumentov --parse-only a --int-only .\n");
				exit(10);
			}
		}
		if ($count_args != $argc)
		{
			fwrite(STDERR, "Použi prepínač '--help' pre zobrazenie nápovedy.\n");
		    exit(10);
		}
	}
}


if($recursive_flag == true)
{	
	$subfolders = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($directory), RecursiveIteratorIterator::SELF_FIRST);
	foreach($subfolders as $dir_source => $object) 
	{
		TestFiles($dir_source);
	}
}
else
{
	foreach (glob($directory."/*.src") as $dir_source) 
	{
    	TestFiles($dir_source);
	}
}

if ($test_count > 0)
{
	$HTML = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">
    <title> TEST.PHP -testovací skript pre IPP projekt </title> <style> td,th { border-collapse:collapse;text-align:center}
    </style></head><body><h1>Výsledky testov</h1><br>"."<h2> $success Testov úspešne prešlo | $failure Testov zlyhalo. (". 100*$success/$test_count."% úspech) </h2> ".$HTML."</tbody></table></body></html>";             
}
else
{
	$HTML = "<html><head><meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">
    <title> TEST.PHP -testovací skript pre IPP projekt </title> <style> td,th { border-collapse:collapse;text-align:left}
    </style></head><body><h1>Výsledky testov</h1><br>".$HTML."</tbody></table></body></html>";
}

echo $HTML;		//vypis vysledného html súboru na STDOUT

?>