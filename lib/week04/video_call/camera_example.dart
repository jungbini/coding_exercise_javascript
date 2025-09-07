import 'package:camera/camera.dart';
import 'package:flutter/material.dart';

late List<CameraDescription> _cameras;

Future<void> main() async {
  // 1. Flutter 앱이 실행 될 준비가 됐는지 확인
  WidgetsFlutterBinding.ensureInitialized();

  // 2. 핸드폰에 있는 카메라들 가져오기
  _cameras = await availableCameras();
  
  runApp(const CameraApp());
}

class CameraApp extends StatefulWidget {
  const CameraApp({Key? key}) : super(key: key);

  State<CameraApp> createState() => _CameraAppState();
}

class _CameraAppState extends State<CameraApp> {
  // 3. 카메라를 제어할 수 있는 컨트롤러 선언
  late CameraController controller;

  void initState() {
    super.initState();

    initializeCamera();
  }

  initializeCamera() async {
    try {
      // 4. 가장 첫 번째 카메라로 카메라 설정하기
      controller = CameraController(_cameras[0], ResolutionPreset.max);

      // 5. 카메라 초기화
      await controller.initialize();

      setState(() { });
      
    } catch (e) {
      // 에러 났을 때 출력
      if (e is CameraException) {
        switch (e.code) {
          case 'CameraAccessDenied':
            break;
          default:
            print('Handle other errors.');
            break;
        }
      }
    }
  }

  void dispose() {
    // 컨트롤러 삭제
    controller.dispose();
    super.dispose();
  }

  Widget build(BuildContext context) {

    // 6. 카메라 초기화 상태 확인
    if (!controller.value.isInitialized) {
      return Container();
    }
    return MaterialApp(  
      // 7. 카메라 보여주기
      home: CameraPreview(controller),
    );
  }
}