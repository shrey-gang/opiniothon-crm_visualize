<?php
	
	$usrnm = $_POST['email'];
	$pass = $_POST['pass'];
	$request = array("emailId"=>$usrnm,"password"=>$pass);
	json_encode($result);
	try{	
		$curl = curl_init (); // $url your URL to send array data
		curl_setopt ($curl, CURLOPT_URL, "http://localhost/check.py");
		curl_setopt ($curl, CURLOPT_POST, true);
		curl_setopt($curl, CURLOPT_POSTFIELDS, $postData); // Your array field
			
		$response = curl_exec ($curl);
		json_decode($response);
		if( $response['result'] == 'success' ){
			//redirect to dashboard
			session_start();
			$_SESSION['client'] = $response['client'];
			header( "refresh:0;url=admin/home.php" );
		}
		else
			//redirect to home page/login page
			echo "<script>alert('Error while signing in!!!!');</script>";
			header( "refresh:0;url=index.php" );
		
		curl_close ($curl);
	}catch(Exception $e){
		echo $e->getMessage();
	}

	
	