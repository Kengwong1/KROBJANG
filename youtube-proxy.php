<?php
// youtube-proxy.php

// 🔑 ใส่ API KEY ของที่รักตรงนี้
$apiKey = "YOUR_API_KEY";

// รับค่า channelId จาก query string
$channelId = isset($_GET['channelId']) ? $_GET['channelId'] : null;

// ถ้าไม่มี channelId ให้หยุดการทำงาน
if (!$channelId) {
    echo json_encode(["error" => "Missing channelId"]);
    exit;
}

// สร้าง URL สำหรับเรียก YouTube API
$apiUrl = "https://www.googleapis.com/youtube/v3/search?key={$apiKey}&channelId={$channelId}&part=snippet,id&order=date&maxResults=12";

// เรียก API
$response = file_get_contents($apiUrl);

// ส่งกลับเป็น JSON
header("Content-Type: application/json; charset=UTF-8");
echo $response;
