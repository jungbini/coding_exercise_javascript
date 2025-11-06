// 함수 표현식으로 변수에 할당
const add = function(a, b) {
    return a + b;
}

// 콜백에 익명 함수
setTimeout(function() {
    console.log('1s')
}, 1000);

// 즉시 실행 함수
(function() {
    console.log('executed')
})();
