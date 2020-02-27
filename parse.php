<?php

/****************************************
*	PARSE.PHP skript pre predmet 		*
*	autor: Boboš Dominik xbobos00		*
*	akademický rok: 2019/2020			*
*	mail: xbobos00@stud.fit.vutbr  		*
****************************************/
declare(strict_types=1);



//////////////	PRE KOMPATIBILITU SYSTÉMOV 	///////////////////
$merlin = strtoupper(substr(PHP_OS, 0, 5));
if (($merlin = strtoupper(substr(PHP_OS, 0, 5))) == "LINUX")
	$merlin_bool = true;
////////// KVÔLI ROZDIELNEMU UKONČOVANIu SÚBOROV //////////////


/************************
*	GLOBÁLNE PREMENNÉ  	*
*************************/
$filepath = "php://stdin";						// vstupný súbor zo stdin
$stdin = fopen($filepath, 'r');					// obsah súboru								
$temp_lex_char = '';							// načítavanie znaku v lexikálnej analýze
$temp_lex_str = '';								// uceleny token zo znakov
$comments_count;								// počítanie komentárov
$instr_count = 0;								// počítanie inštrukcií
$label_count = 0;								// počítanie náveští
$jump_count = 0;								// počítanie skokov
$instr_bool = false;							// bool na správne vypísanie chybovej hlášky
$xml_file;										// premenne potrebné pre generovanie GenerateXML
$xml_prog;										// premenne potrebné pre generovanie GenerateXML
$counting_good = 0;								// overuje správne zadané argumenty
$label_arr = array("");							// pole pre unikatne labels
/************************/
GenerateXML::makeXMLheader();



/****************************************
*	Funkcia na spracovanie 				*
*	chybových hlášok					*
****************************************/
function ErrorExit($exit_code) 
{
	global $stdin;
    fclose($stdin);

    gc_collect_cycles();				//uvoľňuje využité zdroje

    switch ($exit_code) 
    {
    	case "WRONG_PARAM":
    		exit(10);
    		break;
    	case "FILEIN_FAIL":
    		exit(11);
    		break;
    	case "FILEOUT_FAIL":
    		exit(12);
    		break;
    	case "MISSING_HEADER":
    		exit(21);
    		break;
    	case "WRONG_OPCODE":
    		exit(22);
    		break;
    	case "LEX_ERROR":
    		exit(23);
    		break;
    	case "INTERNAL_ERROR":
    		exit(99);
    		break;
    	default:
    		exit(99);				
    }
}



/****************************************
*	Trieda ktorá obsahuje 				*
*	funkcie na generovanie XML súboru	*
****************************************/
class GenerateXML
{
	///						///
	//tvorba hlavičky		 //
	///						///
	public static function makeXMLheader()
	{
		global $xml_file;
		global $xml_prog;

		$xml_file = new DomDocument("1.0", "UTF-8");
		$xml_prog = $xml_file->createElement('program');
		$xml_prog->setAttribute('language', 'IPPcode20');
        $xml_file->appendChild($xml_prog);
	}

	///						///
	//tvorba tela programu	 //
	///						///
	public static function makeXMLprogram()
	{
		global $xml_file;
		global $xml_prog;
		global $instr_count;

		$count = "$instr_count";
		$arg_0 = func_get_arg(0);

		$instr = $xml_file->createElement('instruction');
		$instr->setAttribute('order', $count);
		$instr->setAttribute('opcode', $arg_0);
	
		$arg_count = 1;

		//switch na spracovanie jednotlivých predaných parametrov 
		while($arg_count < func_num_args())
		{
			$token = func_get_arg($arg_count);

			if ($token->keyword === "type")
			{
				$argument = $xml_file->createElement("arg$arg_count", $token->str);
				$argument->setAttribute('type', 'type');
			}
			elseif ($token->keyword === "labelstr")
			{
				$argument = $xml_file->createElement("arg$arg_count", $token->str);
				$argument->setAttribute('type', 'label');
			}
			elseif ($token->keyword === "var")
			{
				$argument = $xml_file->createElement("arg$arg_count", $token->str);
				$argument->setAttribute('type', 'var');
			}
			elseif ($token->keyword === "sint")
			{
				$argument = $xml_file->createElement("arg$arg_count", $token->str);
				$argument->setAttribute('type', 'int');
			}
			elseif ($token->keyword === "snil")
			{
				$argument = $xml_file->createElement("arg$arg_count", $token->str);
				$argument->setAttribute('type', 'nil');
			}
			elseif ($token->keyword === "sbool")
			{
				$argument = $xml_file->createElement("arg$arg_count", $token->str);
				$argument->setAttribute('type', 'bool');
			}
			elseif ($token->keyword === "sstring")
			{
				$argument = $xml_file->createElement("arg$arg_count", $token->str);
				$argument->setAttribute('type', 'string');
			}
			$arg_count++;

			$instr->appendChild($argument);
		}
		$xml_prog->appendChild($instr);
	}
}




/****************************************
*	trieda na spravovanie 				*
*	a uchovanie hodnotov Tokenu			*
****************************************/
class Token
{
    public $keyword;							//použiteľné pre všetky classes
    public $str;								// --||--

    function __Construct($keyword, $str) {
        $this->keyword = $keyword;
        $this->str = $str;
    }
}



/****************************************
*	trieda pre 							*
*	lexikálnu analýzu					*
****************************************/
class Scanner
{
	// kľučové slová jazyka IPPcode20
	public static $keywords = array(
		"MOVE", 
		"CREATEFRAME", 
		"PUSHFRAME", 
		"POPFRAME", 
		"DEFVAR", 
		"CALL", 
		"RETURN", 
		"PUSHS", 
		"POPS", 
		"ADD", 
		"SUB", 
		"MUL", 
		"IDIV", 
		"LT", 
		"GT", 
		"EQ", 
		"AND", 
		"OR", 
		"NOT", 
		"INT2CHAR", 
		"STRI2INT", 
		"READ", 
		"WRITE", 
		"CONCAT", 
		"STRLEN", 
		"GETCHAR", 
		"SETCHAR", 
		"TYPE", 
		"LABEL", 
		"JUMP", 
		"JUMPIFEQ", 
		"JUMPIFNEQ", 
		"EXIT",
		"DPRINT", 
		"BREAK");

	///															///
	//hľadanie kľúčových slov v IPPcode20 , 					 //
	//inkrementácia $instr_count a case insensitive porovnanie 	 //
	///															///
	public static function FoundKeyword() 
	{
        foreach (Scanner::$keywords as $keyword) 
        {
        	global $temp_lex_str;

            if(strcasecmp($temp_lex_str, $keyword) == 0) 		//case insensitive porovnavanie
            {   
            	if ($temp_lex_str == "label") return false;
            	global $instr_count;
          		$instr_count++;									//keyword znamená novú inštrukciu
                $newtoken = new Token($keyword, $keyword);
                return $newtoken;
            }
        }
        return false;
    }


    //získanie znaku zo STDIN
    public function GetChar() 
    {   
    	global $stdin;
    	global $temp_lex_char;
    	

        $temp_lex_char = fgetc($stdin);				// načítava znak zo súboru
        
        //spracovanie komentárov
        if($temp_lex_char === '#') 
        {
        	global $comments_count;
            $comments_count++;						///pocitanie a "mazanie" komentarov
            while (ord($temp_lex_char) != 10) 		///pokym nebude EOL
            {  	
            	$temp_lex_char = fgetc($stdin);

            	global $merlin_bool;
            	if (feof($stdin))
            	{
            		break;
            	}
            }
        }
    }

    ///												///
    //  získavanie jednotlivých tokenov v IPPcode20	 //
    ///												///
    public function GetNextToken()
    {
		global $stdin;
		global $temp_lex_char;
		global $temp_lex_str;
		$newtoken = false;	
		$temp_bool = true;
		
		//menežuje biele znaky
		while($temp_bool != false)
		{
			$temp_bool = false;

			if ($temp_lex_char == "\n") 	//EOL
			{
				$newtoken = new Token("EOL", "EOL");
				Scanner::GetChar();			//nacitaj dalsi 
			}
			elseif (feof($stdin)) 
			{         
                $newtoken = new Token("EOF", "EOF");
            } 
			elseif (ord($temp_lex_char) == 9 or ord($temp_lex_char) == 11 or ord($temp_lex_char) == 13 or ord($temp_lex_char) == 32 ) 	
			{
				Scanner::GetChar();			//nacitaj dalsi znak
				$temp_bool = true;
			}
		}

		while($newtoken == false)
		{ 
			global $merlin_bool;
				//kvôli rozdielnemu ukončovaniu súborov na macu a merlinovi
			if(ctype_space($temp_lex_char) or ((feof($stdin)) and $merlin_bool = true) )	
			{
				switch ($temp_lex_str) 
				{
					//KĽÚČOVÉ SLOVÁ do $newtoken sa v prípade úspechu uloží token
					case (($newtoken = Scanner::FoundKeyword() ) != false):
					{
						$temp_lex_str = '';	//FoundKeyword spravi vsetko potrebne
						break; 	
					}
					//HLAVIČKA
					case (strtoupper($temp_lex_str) == ".IPPCODE20"):
					{
						$newtoken = new Token("header",".IPPcode20");
						$temp_lex_str = '';
						break;
					}
					//NIL symbol
					case (preg_match('/^nil@nil$/', $temp_lex_str) == 1):
					{
						$temp_lex_str = substr($temp_lex_str, 4);
                    	$newtoken = new Token("snil", $temp_lex_str);
                    	$temp_lex_str = '';    
                    	break;
                    }
					//BOOL symbol
					case (preg_match('/^bool@(true|false)$/', $temp_lex_str) == 1):
					{
						$temp_lex_str = substr($temp_lex_str, 5);
                    	$newtoken = new Token("sbool", $temp_lex_str);
                    	$temp_lex_str = '';    
                    	break;
                    }
                    //INT symbol
                    case (preg_match('/^int@[+-]?[0-9]+$/', $temp_lex_str) == 1):
                    {
                    	$temp_lex_str = substr($temp_lex_str, 4);
                    	$newtoken = new Token("sint", $temp_lex_str);
                    	$temp_lex_str = '';    
                    	break;
                    }
                    //STRING symbol - moze obsahovat aj premennu.  'u' nakonci kvôli akceptácií českých znakov 
                    case (preg_match('/^string@([[:alnum:]]|[\_\-\*\$\@\%\&\?\!\;\/\'\,\.\:\=]|\\\\[0-9]{3})*$/u', $temp_lex_str) == 1):	
                    {
						$temp_lex_str = substr($temp_lex_str, 7);
						$newtoken = new Token("sstring", $temp_lex_str);
                    	$temp_lex_str = '';    
                    	break;
                    }
                    //TYP
                    case (preg_match('/^(int|bool|string|nil)$/', $temp_lex_str) == 1):		//checkni potom nil
                    {
						$newtoken = new Token("type", $temp_lex_str);
                    	$temp_lex_str = '';    
                    	break;
                    }
                    //PREMENNÉ
                    case (preg_match('/^(GF|LF|TF)@([[:alpha:]]|[\_\-\*\$\%\&\?\!])([[:alnum:]]|[\_\-\*\$\@\;\%\&\?\!\/])*$/u', $temp_lex_str) == 1):
                    {
						$newtoken = new Token("var", $temp_lex_str);
                    	$temp_lex_str = '';    
                    	break;
                    }
                    //LABEL-  rovnake ako VAR
                    case (preg_match('/^([[:alpha:]]|[\_\-\*\$\%\&\?\!])([[:alnum:]]|[\_\-\*\$\%\@\&\?\!\;\/])*$/u', $temp_lex_str) == 1):
                    {
						$newtoken = new Token("labelstr", $temp_lex_str);
                    	$temp_lex_str = '';    
                    	break;
                    }
					default:
					{
						global $instr_count;
						global $instr_bool;
						if ($instr_count == 0)	//nebola nijaká inštrukcia predtým čiže hlavička je buď chybne alebo nie je
						{
							fwrite(STDERR, "Chybne napísaná hlavička .IPPcode20!\n");
            				ErrorExit("MISSING_HEADER");
						}
						elseif ($instr_count != 0 and $instr_bool == true)
						{
							fwrite(STDERR, "Chybne napísaná alebo neexistujúca inštrukcia!\n");
            				ErrorExit("WRONG_OPCODE");
						}

						fwrite(STDERR, "Lexikálna chyba!\n");
						ErrorExit("LEX_ERROR");
					}
				}
			}
			else
			{
				// modifikácia problematických znakov v XML
				if ($temp_lex_char == '<'){
					$temp_lex_str = $temp_lex_str . "&lt;";
				}
				elseif ($temp_lex_char == '>'){
					$temp_lex_str = $temp_lex_str . "&gt;";
				}
				elseif ($temp_lex_char == '&'){
					$temp_lex_str = $temp_lex_str . "&amp;";
				}
				else{
					$temp_lex_str = $temp_lex_str . $temp_lex_char;
				}
				
				if (feof($stdin)) 
				{            
             	   $newtoken = new Token("EOF", "EOF");
            	}
            	else 
					Scanner::GetChar();
					
			}
		}
		return $newtoken;
    }
}



/****************************************
*	Syntaktická analýza					*
*	a generovanie XML 					*
****************************************/
class SyntaxAnalysis
{
	///											///
	// kontrola tokenov pre platnosť pravidiel 	 //
	///											///
	public function CheckToken($keyword, $str)
	{
		global $temp_lex_char;
		global $temp_lex_str;

		$check_token = Scanner::GetNextToken();

		//osetrovanie ze v symb moze byt aj var
        if($check_token->keyword == "sint" or $check_token->keyword == "snil" or
        	$check_token->keyword == "sbool" or $check_token->keyword == "sstring") 
        {
            $temp_keyword = "symb";	
        } 
        else 
        {
            $temp_keyword = $check_token->keyword;	//pomocna premenná na uchovanie kľúčového slova
        }


        if($keyword == '' and $str == '') 
        {
        	fwrite(STDERR, "Interná chyba v prekladači!\n");
            ErrorExit("INTERNAL_ERROR");
        } 
        elseif($keyword != '' and $str == '') 
        {
            if(strcmp($keyword, $temp_keyword) != 0) 	//ak som očakával 'symb' ale token bol 'var'
            {
                if ($keyword == 'symb' and $temp_keyword == 'var') 
                {    
                	;
                } 
                else
                {
                	
                	if ($keyword == 'EOL' and $temp_keyword == 'EOF')
                		;

                	else
                	{
                	//	fwrite(STDERR, "Syntaktická chyba!\n");
                    	ErrorExit("LEX_ERROR");
                    }
                } 
            }
        } 
        elseif($str != '')  
        {
            if(strcmp($str, $check_token->str) != 0)
            {
            	if($str == '.IPPcode20')
            	{
            		if ($check_token->str === "EOL" )
            		{
            			SyntaxAnalysis::CheckToken('','.IPPcode20');
            		}
            		else
            		{
            			fwrite(STDERR, "Chýbajúca hlavička .IPPcode20!\n");
            			ErrorExit("MISSING_HEADER");
            		}
            	}
            	else
            	{
            		global $merlin_bool;
            		if ($str == 'EOL' and $check_token->str == 'EOF' and $merlin_bool == true)
                		;
	            	else
	            	{
	            	//	fwrite(STDERR, "Syntaktická chyba!\n");
	                	ErrorExit("LEX_ERROR");
	                }
            	}
            } 
        }
        return $check_token;
	}
	///																		///
	//  spracovanie pravidla Instruction a následné správne volanie funkcie	 //
	///																		///
	function Instruction()
	{
		global $temp_lex_char;
		global $temp_lex_str;
		global $stdin;
		global $instr_bool;

		$instr_bool = true;
		$token = Scanner::GetNextToken();
		$instr_bool = false;
 
		// switch-case jednotlivých inštrukcií IPPcode20 a následné volanie funkcie danej inštrukcie
		switch (strtoupper($token->keyword))		//sú case insensitive
		{
			case "EOL":								// v pripade ze mame prazdne riadky 
				SyntaxAnalysis::Instruction();
				break;
			case "MOVE":
				SyntaxAnalysis::RuleMove();
				break;
			case "CREATEFRAME":
				SyntaxAnalysis::RuleCreateframe();
				break;
			case "PUSHFRAME":
				SyntaxAnalysis::RulePushframe();
				break;
			case "POPFRAME":
				SyntaxAnalysis::RulePopframe();
				break;
			case "DEFVAR":
				SyntaxAnalysis::RuleDefvar();
				break;
			case "CALL":
				SyntaxAnalysis::RuleCall();
				break;
			case "RETURN": 
				SyntaxAnalysis::RuleReturn();
				break;
			case "PUSHS": 
				SyntaxAnalysis::RulePushs();
				break;
			case "POPS": 
				SyntaxAnalysis::RulePops();
				break;
			case "ADD": 
				SyntaxAnalysis::RuleAdd();
				break;
			case "SUB": 
				SyntaxAnalysis::RuleSub();
				break;
			case "MUL": 
				SyntaxAnalysis::RuleMul();
				break;
			case "IDIV": 
				SyntaxAnalysis::RuleIdiv();
				break;
			case "LT":
				SyntaxAnalysis::RuleLT();
				break;
			case "GT": 
				SyntaxAnalysis::RuleGT();
				break;
			case "EQ": 
				SyntaxAnalysis::RuleEQ();
				break;
			case "AND": 
				SyntaxAnalysis::RuleAND();
				break;
			case "OR":
				SyntaxAnalysis::RuleOR();
				break;
			case "NOT": 
				SyntaxAnalysis::RuleNOT();
				break;
			case "INT2CHAR": 
				SyntaxAnalysis::RuleInt2char();
				break;
			case "STRI2INT": 
				SyntaxAnalysis::RuleStri2int();
				break;
			case "READ":
				SyntaxAnalysis::RuleRead();
				break;
			case "WRITE": 
				SyntaxAnalysis::RuleWrite();
				break;
			case "CONCAT": 
				SyntaxAnalysis::RuleConcat();
				break;
			case "STRLEN": 
				SyntaxAnalysis::RuleStrlen();
				break;
			case "GETCHAR": 
				SyntaxAnalysis::RuleGetchar();
				break;
			case "SETCHAR": 
				SyntaxAnalysis::RuleSetchar();
				break;
			case "TYPE": 
				SyntaxAnalysis::RuleType();
				break;
			case "LABEL": 
				SyntaxAnalysis::RuleLabel();
				break;
			case "JUMP":
				SyntaxAnalysis::RuleJump();
				break;
			case "JUMPIFEQ": 
				SyntaxAnalysis::RuleJumpifeq();
				break;
			case "JUMPIFNEQ": 
				SyntaxAnalysis::RuleJumpifneq();
				break;
			case "EXIT":
				SyntaxAnalysis::RuleExit();
				break;
			case "DPRINT": 
				SyntaxAnalysis::RuleDprint();
				break;
			case "BREAK":
				SyntaxAnalysis::RuleBreak();
				break;
			default:
				if ($token->keyword == "EOF")
					; 	//koniec instrukcii mam EOF
				else
				{
					fwrite(STDERR, "Chybná/Nesprávna inštrukcia!\n");
	        		ErrorExit("WRONG_OPCODE");
				}
		}
	}


	///											///
	// 		Spracovanie jednotlivých pravidiel	 //
	//		a následné volanie funkcie pre 		 //
	//		generovanie XML výstupu				 //
	///											///
	//spracovanie prvého pravidla
	public function parse()
	{
	//	.IPPcode20 EOL <Instruction> EOF
		SyntaxAnalysis::CheckToken('','.IPPcode20');
		SyntaxAnalysis::CheckToken('EOL','EOL');
		SyntaxAnalysis::Instruction();
		SyntaxAnalysis::CheckToken('EOF','EOF');

	}
	//MOVE <var> <symb> EOL <Instruction>
	function RuleMove()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("MOVE", $argument1, $argument2);

		SyntaxAnalysis::Instruction();
	}
	// CREATEFRAME EOL <Instruction>
	function RuleCreateframe()
	{
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("CREATEFRAME");

		SyntaxAnalysis::Instruction();
	}
	// PUSHFRAME EOL <Instruction>
	function RulePushframe()
	{
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("PUSHFRAME");

		SyntaxAnalysis::Instruction();
	}
	// POPFRAME EOL <Instruction>
	function RulePopframe()
	{
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("POPFRAME");

		SyntaxAnalysis::Instruction();
	}
	// DEFVAR <var> EOL <Instruction>
	function RuleDefvar()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("DEFVAR", $argument1);

		SyntaxAnalysis::Instruction();
	}
	// CALL <label> EOL <Instruction>
	function RuleCall()
	{
		$argument1 = SyntaxAnalysis::CheckToken('labelstr','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("CALL", $argument1);
		global $jump_count;
		$jump_count++;

		SyntaxAnalysis::Instruction();
	}
	// RETURN EOL <Instruction>
	function RuleReturn()
	{
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("RETURN");
		global $jump_count;
		$jump_count++;

		SyntaxAnalysis::Instruction();
	}
	//PUSHS <symb> EOL <Instruction>
	function RulePushs()
	{
		$argument1 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("PUSHS", $argument1);

		SyntaxAnalysis::Instruction();
	}
	// POPS <var> EOL <Instruction>
	function RulePops()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("POPS", $argument1);

		SyntaxAnalysis::Instruction();
	}
	// ADD <var> <symb1> <symb2> EOL <Instruction>
	function RuleAdd()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("ADD", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// SUB <var> <symb1> <symb2> EOL <Instruction>
	function RuleSub()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("SUB", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// MUL <var> <symb1> <symb2> EOL <Instruction>
	function RuleMul()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("MUL", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// IDIV <var> <symb1> <symb2> EOL <Instruction>
	function RuleIdiv()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("IDIV", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// LT <var> <symb1> <symb2> EOL <Instruction>
	function RuleLT()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("LT", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	//  GT <var> <symb1> <symb2> EOL <Instruction>
	function RuleGT()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("GT", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// EQ <var> <symb1> <symb2> EOL <Instruction>
	function RuleEQ()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("EQ", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// AND <var> <symb1> <symb2> EOL <Instruction>
	function RuleAND()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("AND", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// OR <var> <symb1> <symb2> EOL <Instruction>
	function RuleOR()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("OR", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// NOT <var> <symb1> EOL <Instruction>
	function RuleNOT()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("NOT", $argument1, $argument2);

		SyntaxAnalysis::Instruction();
	}
	// INT2CHAR <var> <symb> EOL <Instruction>
	function RuleInt2char()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("INT2CHAR", $argument1, $argument2);

		SyntaxAnalysis::Instruction();
	}
	// STRI2INT <var> <symb1> <symb2> EOL <Instruction>
	function RuleStri2int()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("STRI2INT", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// READ <var> <type> EOL <Instruction>
	function RuleRead()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('type','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("READ", $argument1, $argument2);

		SyntaxAnalysis::Instruction();
	}
	// WRITE <symb> EOL <Instruction>
	function RuleWrite()
	{
		$argument1 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("WRITE", $argument1);

		SyntaxAnalysis::Instruction();
	}
	// CONCAT <var> <symb1> <symb2> EOL <Instruction>
	function RuleConcat()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("CONCAT", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	// STRLEN <var> <symb> EOL <Instruction>
	function RuleStrlen()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("STRLEN", $argument1, $argument2);

		SyntaxAnalysis::Instruction();
	}
	// GETCHAR <var> <symb1> <symb2> EOL <Instruction>
	function RuleGetchar()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("GETCHAR", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}
	//SETCHAR <var> <symb1> <symb2> EOL <Instruction>
	function RuleSetchar()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("SETCHAR", $argument1, $argument2, $argument3);

		SyntaxAnalysis::Instruction();
	}	
	//TYPE <var> <symb> EOL <Instruction>
	function RuleType()
	{
		$argument1 = SyntaxAnalysis::CheckToken('var','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("TYPE", $argument1, $argument2);

		SyntaxAnalysis::Instruction();
	}
	// LABEL <label> EOL <Instruction>
	function RuleLabel()
	{
		
		$argument1 = SyntaxAnalysis::CheckToken('labelstr','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("LABEL", $argument1);
		global $label_count, $label_arr;

		if (in_array($argument1->str,$label_arr))
			;
		else
		{
			$label_count++;
			$label_arr[] = $argument1->str;
		}


		SyntaxAnalysis::Instruction();
	}
	// JUMP <label> EOL <Instruction>
	function RuleJump()
	{
		$argument1 = SyntaxAnalysis::CheckToken('labelstr','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("JUMP", $argument1);
		global $jump_count;
		$jump_count++;

		SyntaxAnalysis::Instruction();
	}
	// JUMPIFEQ <label> <symb1> <symb2> EOL <Instruction>
	function RuleJumpifeq()
	{
		$argument1 = SyntaxAnalysis::CheckToken('labelstr','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("JUMPIFEQ", $argument1, $argument2, $argument3);
		global $jump_count;
		$jump_count++;

		SyntaxAnalysis::Instruction();
	}
	// JUMPIFNEQ <label> <symb1> <symb2> EOL <Instruction>
	function RuleJumpifneq()
	{
		$argument1 = SyntaxAnalysis::CheckToken('labelstr','');
		$argument2 = SyntaxAnalysis::CheckToken('symb','');
		$argument3 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("JUMPIFNEQ", $argument1, $argument2, $argument3);
		global $jump_count;
		$jump_count++;

		SyntaxAnalysis::Instruction();
	}
	// EXIT <symb> EOL <Instruction>
	function RuleExit()
	{
		$argument1 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("EXIT", $argument1);

		SyntaxAnalysis::Instruction();
	}
	//DPRINT <symb> EOL <Instruction>
	function RuleDprint()
	{
		$argument1 = SyntaxAnalysis::CheckToken('symb','');
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("DPRINT", $argument1);

		SyntaxAnalysis::Instruction();
	}
	// BREAK EOL <Instruction>
	function RuleBreak()
	{
		SyntaxAnalysis::CheckToken('EOL','EOL');

		GenerateXML::makeXMLprogram("BREAK");

		SyntaxAnalysis::Instruction();
	}
}


/****************************************
*				  MAIN 	 				*
****************************************/
// ak nebol zadaný nijaký prepínač
if($argc == 1)
{
	Scanner::GetChar();
	SyntaxAnalysis::parse();
}
else
{
    $long_params = array(
        "help",
        "stats:",
        "loc",
        "comments",
        "jumps",
        "labels"
    );

	$params = getopt ( "", $long_params);		//zíkanie argumentov a ich parsovanie do $params

	if (array_key_exists('help', $params) )
	{
		if($argc == 2) 							// zadany argument --help
		{
            echo <<<EOL
-Skript parse.php prekladá vstupný súbor napísaný v jazyku IPPcode20 
do výstupného XML formátu, s ktorým ďalej pracuje interpret.py
-vstupný súbor sa presmerováva pomocou '<' na stdin
- § php parse.php <vstupnysubor.txt
-XML formát sa vypisuje na stdout
- --stats="súbor" vypisuje štatistiku do "súbor"
- --loc používaný spoločne s --stats, vypisuje počet riadkov kódu do "súbor" 
- --comments používaný spoločne s --stats, vypisuje počet komentárov 
v kóde do "súbor"
- --labels používaný spoločne s --stats, vypisuje počet definovaných náveští
do "súbor"
- --jumps používaný spoločne s --stats, vypisuje počet 
podmienených/nepodmienených skokov, volania a návraty z volania do "súbor"

EOL;
            exit(0);
        } 
        else 
        {
        	fwrite(STDERR, "Použi samostatne prepínač '--help' pre zobrazenie nápovedy.\n");
            ErrorExit("WRONG_PARAM");
        }
	}
	elseif (array_key_exists("stats", $params))							//rozsirenie STATP
	{
		$statistics_file = fopen($params["stats"], "w");
		if ($statistics_file == false)
		{
			fwrite(STDERR, "Výstupný súbor nejde otvoriť alebo neexituje!\n");
			ErrorExit("FILEOUT_FAIL");
		}
        // if ($argc < 3)
        // {
        // 	fwrite(STDERR, "Nesprávny počet argumentov! Použi prepínač '--help' pre zobrazenie nápovedy.\n");
        // 	ErrorExit("WRONG_PARAM");
        // }
        Scanner::GetChar();
		SyntaxAnalysis::parse();

		global $comments_count;
		global $instr_count;
		global $label_count;
		global $jump_count;
		global $counting_good;

		for ($i=1; $i <= $argc; $i++) 
		{ 

			switch ($argv[$i]) 
			{
				case "--loc":
					global $statistics_file;
					fwrite($statistics_file, "$instr_count\n");
					$counting_good++;
					break;
				case "--comments":
					global $statistics_file;
					fwrite($statistics_file, "$comments_count\n");
					$counting_good++;
					break;
				case "--labels":
					global $statistics_file;
					fwrite($statistics_file, "$label_count\n");
					$counting_good++;
					break;
				case "--jumps":
					global $statistics_file;
					fwrite($statistics_file, "$jump_count\n");	
					$counting_good++;				
					break;
				case "stats":
					break;
				default:
					;
			}
		}
	}
	else
	{
		fwrite(STDERR, "Použi prepínač '--help' pre zobrazenie nápovedy.\n");
        ErrorExit("WRONG_PARAM");
	}
}
global $xml_file;


//Testujem či neboli zadané nesprávne argumenty
if ($argc != ($counting_good +2) and $argc != 1)
{
	fwrite(STDERR, "Nesprávny zadané argumenty! Použi prepínač '--help' pre zobrazenie nápovedy.\n");
	ErrorExit("WRONG_PARAM");
}

$xml_file->formatOutput = true;
echo $xml_file->saveXML();
fclose($stdin);
if ($argc > 2)	
{
	fclose($statistics_file);
}
return 0;

?>
