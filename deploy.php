<?php
error_log('File accessed');
if($json = json_decode(file_get_contents("php://input"), true)) {
    $data = $json;
	error_log('php://input');

} else {
   $data = $_POST;
   error_log('POST used');
}

$ref = $data['ref'] ?? "";

function replace_spaces($var_replace) {
	return str_replace('__', ' ', $var_replace);
}

$should_override = false;
if ($ref == 'refs/heads/main' || $should_override == true) {
	$firstMsg = 'Executing git pull';
	error_log($firstMsg);
	echo $firstMsg;
	// First command is to PULL
	$status = shell_exec("git pull origin main -f");
	error_log($status);
	echo $status;
	// Second command is to enter the source and install requirements
	$source = $_SERVER['SOURCE_ENV'];
	$source = replace_spaces($source);

	$sourceCmd = "{$source} && pip install -r requirements.txt";
	$secondMsg = 'Executing source cmd';
	error_log($secondMsg);
	echo $secondMsg;
	$status = shell_exec($sourceCmd);
	error_log($status);
	echo $status;

	// Third command is to update the file
	$restartCmd = $_SERVER['RESTART_FILE_PATH'];
	$thirdMsg = 'Executing restart cmd';
	error_log($thirdMsg);
	echo $thirdMsg;
	$status = shell_exec("echo $(date) > " . $restartCmd);
	error_log($status);
	echo $status;
}
