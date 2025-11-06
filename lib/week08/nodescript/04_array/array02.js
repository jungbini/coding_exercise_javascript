const students = [
    { name: 'Alice', age: 10 }, {name: 'Bob', age: 20}, {name: 'Catherine', age: 30}
];

const nameArray = students.map(function(person) {
    return person.name;
});
console.log(nameArray);

const under20 = students.filter(function(person) {
    return person.age <= 20;
});
console.log(under20);
