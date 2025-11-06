const args = [1, 2, 3];

function add(x, y, z) {
    return x + y + z;
}
console.log( add(...args) );	// 함수의 인수에도 이용
