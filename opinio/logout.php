<?php
	session_start();
     if( isset($_SESSION['client']) ){
	 	session_destroy();
		 setcookie("PHPSESSID","",time()-3600,"/"); // delete session cookie
		 header( "refresh:0;url=index.php" );
	 }else
	 	header( "refresh:0;url=index.php" );