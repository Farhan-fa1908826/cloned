console.log("hello world");


const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

const video = document.getElementById('video-element');
const image = document.getElementById('img-element');
const captureBtn = document.getElementById('capture-btn');
const reloadBtn = document.getElementById('reload-btn');

reloadBtn.addEventListener('click', function() {
    window.location.reload();
});

if(navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({video: true})
    .then(function(stream) {
        video.srcObject = stream;
        const { width, height } = stream.getTracks()[0].getSettings();
        captureBtn.addEventListener('click', function() {
            captureBtn.style.display = 'none';
            const track = stream.getVideoTracks()[0];
            const imageCapture = new ImageCapture(track);
            console.log(imageCapture);
            imageCapture.takePhoto().then((blob) => {
                    // image.src = URL.createObjectURL(blob);
                    // image.style.display = 'block';
                    // track.stop();

                    const img  = new Image(width,height);
                    img.src = URL.createObjectURL(blob);
                    image.append(img);
                    video.style.display = 'none';
                    console.log("took photo", blob);

                    const reader = new FileReader();
                    reader.readAsDataURL(blob);
                    reader.onloadend = function() {
                        const base64data = reader.result;
                        console.log(base64data);

                        const fd = new FormData();
                        fd.append('csrfmiddlewaretoken', csrftoken);
                        fd.append('photo', base64data);

                        $.ajax({
                            type: 'POST',
                            url: 'classify/',
                            enctype: 'multipart/form-data',
                            data: JSON.stringify({ photo: base64data, csrfmiddlewaretoken: csrftoken }),
                            processData: false,
                            contentType: false,

                            success: (resp) => {
                                console.log(resp);
                                // print(success)
                                if (resp.success){
                                    // window.location.href = window.location.origin;
                                    window.location.href = window.location.origin;
                                }
                                else{
                                    alert(resp.message)
                                    if (resp.message == 'Maximum attempts reached. Session ended.'){
                                        window.location.href = '/';
                                    }
                                    else{
                                        window.location.href = '/auth/facial_recognition/';
                                    }
                                }
                                // window.location.href = '/helios_auth/login/'
                            },
                            error: (err) => {
                                console.log(err);
                            },
                        })

                    }
                }
            )
    });
});
}

