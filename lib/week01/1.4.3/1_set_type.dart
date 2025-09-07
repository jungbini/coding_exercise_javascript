void main() {
  Set<String> blackPink = {'로제', '지수', '리사', '제니', '제니'}; // 1 제니 중복

  print(blackPink);
  print(blackPink.contains('로제'));  // 2 값이 있는지 확인하기
  print(blackPink.toList());         // 3 리스트로 변환하기

  List<String> blackPink2 = ['로제', '지수', '지수'];
  print(Set.from(blackPink2));  // 4 List 타입을 Set 타입으로 변환
}
