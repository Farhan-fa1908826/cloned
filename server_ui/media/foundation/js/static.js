




document.addEventListener('DOMContentLoaded', function () {
    // print(document.title)
    console.log(window.location.pathname);
    if(window.location.pathname == '/'){
        const what_and_why = document.querySelector('.what-and-why');
        what_and_why.addEventListener('click', function() {
            what_and_why.style.display = 'none';
        })
    }
    else if(window.location.pathname == '/faq'){
            const question_container = document.querySelectorAll('.question-container');
            const expanders = document.querySelectorAll('.expander-text');
            const answers = document.querySelectorAll('.answer');
            question_container.forEach((q,index) => {
                q.addEventListener('click', () => {
                console.log(answers[index].style.height);
                if(answers[index].style.height == '0px'){
                    // answers[index].style.height = '100%';
                    answers[index].style.height = answers[index].scrollHeight + 'px';
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