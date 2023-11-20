




document.addEventListener('DOMContentLoaded', function () {
    // print(document.title)
    // console.log(window.location.pathname);
    if(window.location.pathname == '/'){
        const logged = document.querySelector('.logged');
        console.log(window.location.pathname);
        const what_and_why_container = document.querySelector('.large-9');
        const logged_right_box = document.querySelector('.logged-right-box');
        if(logged.textContent == "Logout"){
            console.log("User is logged in");
            // what_and_why_container.style.display = 'none';
            // logged_right_box.style.borderright = 'none';
            logged_right_box.classList.add('logged-right-box-logged');
            what_and_why_container.classList.add('what-and-why-logged');
        }
        // const what_and_why_container = document.querySelector('.what-and-why');
        // what_and_why.addEventListener('click', function() {
        //     what_and_why.style.display = 'none';
        // })
    }
    else if(window.location.pathname == '/faq'){
            const question_container = document.querySelectorAll('.question-container');
            const expanders = document.querySelectorAll('.expander-text');
            const answers = document.querySelectorAll('.answer');
            question_container.forEach((q,index) => {
                q.addEventListener('click', () => {
                console.log(answers[index].style.height);
                if(answers[index].style.height == '0px' || answers[index].style.height == ''){
                    // answers[index].style.height = '100%';
                    answers[index].style.height = answers[index].scrollHeight + 'px';
                    // q.style.height = 'fit-content';
                    // answer.style.display= 'block';
                    expanders[index].style.transform = "rotate(180deg)";
                }else{
                    answers[index].style.height = '0px';
                    // answer.style.transition = '0.3s ease-in-out';
                    expanders[index].style.transform = "none";
                    expanders[index].style.transition = '0.2s ease-in-out';
                }
            });
        });
    }

});