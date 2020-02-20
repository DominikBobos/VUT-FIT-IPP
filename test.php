<?php

declare(strict_types=1);


$directory = getcwd();
$int_file = $directory . "/interpret.py";
$parse_file = $directory . "/parse.php";
$jexamxml_file = "/pub/courses/ipp/jexamxml/jexamxml.jar";

$recursive_flag = false;
$parse_only_flag = false;
$int_only_flag = false;

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

	foreach ($params as $arg => $option) 
	{ 
		if ($arg =='directory')							
		{
			global $directory;
			$tmp_directory = realpath($option);
			echo $tmp_directory;
			if ($tmp_directory == false)	
				exit(11);
							
			$directory = $tmp_directory;	
			echo $directory;	
		}
		elseif ($arg =='recursive')
		{
			global $recursive_flag;
			$recursive_flag = true;
		}
		elseif ($arg =='parse-script')
		{
			global $parse_file;
			if (is_file($option) == false)
				exit(11);
			$parse_file = $option;
			echo $parse_file;
		}
		elseif ($arg =='int-script')
		{
			global $int_file;
			if (is_file($option) == false)
				exit(11);
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
				exit(11);
			$jexamxml_file = $option;
		}
		else
		{
			fwrite(STDERR, "Použi prepínač '--help' pre zobrazenie nápovedy.\n");
	        exit(10);
		}

		if (array_key_exists('parse-only', $params) and array_key_exists('int-only',$params))
			fwrite(STDERR, "Chyba! Kombinovanie argumentov --parse-only a --int-only .\n");
			exit(10);
	}
}


function TestFiles($source)
{
	global $int_file;
	global $parse_file;
	global $jexamxml_file;

	global $parseArg,$interpArg;
	if(substr($source, -2) == ".." || substr($source, -1) == ".")
	{
		return False;
	}
	if(substr($source, -4) == ".src")
	{
		$Name =substr($source, 0,-4);
		$ref_output = str_replace(".src",".out",$source);
		$ref_rc = str_replace(".src",".rc",$source);
		//$in = str_replace(".src",".in",$source);	//zatial nema vyznam ked nemam interpret.py

		if(!file_exists($ref_output))
		{
			fwrite(STDERR, "Referenčný output sa nenachádza v priečinku\n");
			exit(11);
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

		exec("php3.7 ".$parse_file ." <$source >Temp_output", $result,$rc_out);
		if($rc_out != $exp_rc)
		{
			;//HtmlAdd($Name,False,"Chyba Parseru",0,0);		//rc sa nerovnali
		}
		else 
		{
			exec("java -jar ".$jexamxml_file." Temp_output ".$ref_output); //otestovat!!!
			$diff_ret = exec("$?");
			if($diff_ret == 1)
		 	{
				//HtmlAdd($Name,False,"Interpret output match error",0,0);
			}
			else
			{
				echo "dva subory su rovnake brasko";
				//HtmlAdd($Name,True,"Diff",0,0);
			}
		}

		//TODO - REKURZIA A VOLANIE TEJTO FUNKCIE ,GENEROVANIE HTML -thats all

		unlink("Temp_output");
	} 
	return True;	
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




?>