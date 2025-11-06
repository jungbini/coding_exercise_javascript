const obj = {
    greeting: 'hello',
    foo: {
        bar: 'baz'
    },
    now: new Date(),
    func: function() {
        console.log('function');
    }
}
console.log(obj.greeting);	// hello
console.log(obj['greeting']);	// hello
console.log(obj.foo.bar);	// baz
console.log(obj.now);		// 현재 시각
