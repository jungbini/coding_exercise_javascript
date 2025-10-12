import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:async';                        // async 패키지 불러오기

// 1. StatefulWidget 정의
class HomeScreen extends StatefulWidget {
  
  const HomeScreen({Key? key}) : super(key: key);

  State<HomeScreen> createState() => _HomeScreenState();
}

// 2. _HomeScreenState 정의
class _HomeScreenState extends State<HomeScreen> {

  // PageController 생성
  final PageController pageController = PageController();

  // 3. initState() 함수 등록
  void initState() {
    super.initState();      // 부모 initState() 실행

    Timer.periodic(         // Timer.periodic() 등록
      Duration(seconds: 3),
      (timer) {
        // 현재 페이지 가져오기
        int? nextPage = pageController.page?.toInt();

        // 페이지 값이 없을 때 예외 처리
        if (nextPage == null) {
          return;
        }

        // 첫 페이지와 마지막 페이지 분기 처리
        if (nextPage == 4) {
          nextPage = 0;
        } else {
          nextPage++;
        }

        // 자동 페이지 변경
        pageController.animateToPage(  
          nextPage, duration: Duration(milliseconds: 500), curve: Curves.ease,
        );
      },
    );
  }

  Widget build(BuildContext context) {
    
    // 상태바 색상 변경
    // 상태바가 이미 흰색이면 light 대신 dark로 검정으로 바꿔보기
    SystemChrome.setSystemUIOverlayStyle(SystemUiOverlayStyle.light);
    
    return Scaffold(  
      body: PageView(                 // PageView 추가
        controller: pageController,
        children: [1, 2, 3, 4, 5]     // 샘플 리스트 생성
          .map(                       // 위젯으로 매핑
            (number) => Image.asset(
              'asset/img/image_$number.jpeg',
              fit: BoxFit.cover,
            ),            
          )
          .toList(),
      ),
    );
  }
}