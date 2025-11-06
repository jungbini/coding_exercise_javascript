const [first, second, ...foo] = [10, 20, 30, 40, 50];
console.log(first);		// 10
console.log(second);	// 20
console.log(foo);		// [30, 40, 50]

const { a, b, ...bar } = { a: 10, b: 20, c: 30, d: 40 };
console.log(a);	// 10
console.log(b);	// 20
console.log(bar);	// { c: 30, d: 40 }
