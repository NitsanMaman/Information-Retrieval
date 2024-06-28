function loadStudent(index) {
    fetch('students-data/students.json')
        .then(response => response.json())
        .then(data => {
            const students = data.students;
            const student = students[index];

            document.getElementById('student-name').innerText = student.name;
            const emailElement = document.getElementById('student-email');
            emailElement.innerText = student.email;
            emailElement.href = `mailto:${student.email}`;
            document.getElementById('student-hobbies').innerText = student.hobbies.join(', ');

            const coursesList = document.getElementById('student-courses');
            coursesList.innerHTML = ''; // Clear existing list items
            student.courses.forEach(course => {
                const listItem = document.createElement('li');
                listItem.innerText = course;
                listItem.className = 'list-group-item';
                coursesList.appendChild(listItem);
            });

            const imageElement = document.getElementById('student-image');
            imageElement.src = `images/${student.name.split(' ')[0]}Human.png`;
        })
        .catch(error => console.error('Error loading JSON:', error));
}
