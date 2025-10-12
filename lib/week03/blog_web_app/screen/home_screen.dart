import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class HomeScreen extends StatelessWidget {
  
  // WebViewController 선언
  WebViewController webViewController = WebViewController()

    // WebViewController의 loadRequest() 함수 실행
    ..loadRequest(Uri.parse('https://blog.codefactory.ai'))

    // Javascript가 제한 없이 실행될 수 있도록 함
    .. setJavaScriptMode(JavaScriptMode.unrestricted);
   
  HomeScreen({Key? key}): super(key: key);

  Widget build(BuildContext context) {
    return Scaffold(
      // 앱바 위젯 추가
      appBar: AppBar(  
        
        // 배경색 지정
        backgroundColor: Colors.orange,

        // 앱 타이틀 설정
        title: Text('Code Factory'),
        
        // 가운데 정렬
        centerTitle: true,        

        // AppBar에 액션 버튼 추가
        actions: [  
          IconButton(  
            
            // 아이콘을 눌럭씅ㄹ 때 실행할 콜백 함수
            onPressed: () {

              // 웹뷰 위젯에서 사이트 전환하기
              webViewController.loadRequest(Uri.parse('https://dhil.sunmoon.ac.kr'));
            },

            icon: Icon(  
              Icons.home,
            ),
          ),
        ],
      ),

      body: WebViewWidget(
        controller: webViewController,
      )
      
    );
  }
}