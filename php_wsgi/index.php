<?php 
    $name = explode("=",$_SERVER['QUERY_STRING']);
    echo "hi $name[1]";
