const arr = [ 'foo', 'bar', 'baz' ];

for (let i = 0; i < arr.length; i++) {	// C 언어 문법
    console.log(arr[i]);
}

arr.forEach((element) => {		// forEach 함수 사용
    console.log(element);
});

for (const element of arr) {		// ES6 이후 (비동기 처리도 가능)
    console.log(element);
}
