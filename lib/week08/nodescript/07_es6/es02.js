const obj1 = { a: 'aaa', b: 'bbb' };
const obj2 = { c: 'ccc' };
const obj3 = { ...obj1, ...obj2 };

console.log(obj3);		// { a: 'aaa', b: 'bbb', c: 'ccc' }

obj1.c = 'ccc';		// 다른 방법
console.log(obj1);
