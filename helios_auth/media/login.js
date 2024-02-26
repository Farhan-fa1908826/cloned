// console.log('{{ user_json|escapejs }}');
// var userData = JSON.parse(user_json|escapejs);
// console.log("FROM LOGIN JS " +  userData.server_user_face_share);
// if (userData.server_user_face_share && userData.server_user_face_share != "") {
//     var formHTML = `
//         <form method="post" enctype="multipart/form-data">
//             <input type="file" name="file1">
//             <input type="file" name="file2">
//             <input type="submit" value="Submit">
//         </form>
//     `;
//     var container = document.getElementById('formContainer');
//     container.innerHTML = formHTML;
// }

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
};

const component = document.getElementsByTagName("face-liveness")[0];

function listener(event) {
  if (
    event.detail.action === "PROCESS_FINISHED" &&
    event.detail.data.status === 1
  ) {
    // hoow to get the user in the session
    const response = event.detail.data.response;

    if (userData.server_user_face_share) {
      component.style.display = "none";
      var formHTML = `
                <form id="share_form" method="post" enctype="multipart/form-data">
                    <input type="file" name="file1">
                    <input type="file" name="file2">
                    <input type="file" name="file3">
                    <input type="submit" value="Submit">
                </form>
            `;

      var container = document.getElementById("formContainer");
      container.innerHTML = formHTML;



      document
        .getElementById("share_form")
        .addEventListener("submit", function (event) {
          event.preventDefault();

          var file1 = this.elements.file1.files[0];
          var file2 = this.elements.file2.files[0];
          var file3 = this.elements.file3.files[0];

          var reader1 = new FileReader();
          var reader2 = new FileReader();
          var reader3 = new FileReader();

          reader1.onload = function (event) {
            var file1Content = event.target.result;
            var file1ArrayInitial = file1Content.split(" "); // Assuming each line contains a number
            var lastElement1 = file1ArrayInitial[file1ArrayInitial.length - 1];
            var file1Array = file1ArrayInitial.slice(0, -1).map(Number);
            file1Array.push(lastElement1);


            reader2.onload = function (event) {
              var file2Content = event.target.result;
              var file2ArrayInitial = file2Content.split(" "); // Assuming each line contains a number
              var lastElement2 = file2ArrayInitial[file2ArrayInitial.length - 1];
              var file2Array = file2ArrayInitial.slice(0, -1).map(Number);
              file2Array.push(lastElement2);
  

              reader3.onload = function (event) {
                var file3Content = event.target.result;
                var file3Array = file3Content.split(" ").map(Number); // Assuming each line contains a number
    

                $.ajax({
                  type: "POST",
                  url: "../recombine_shares/",
                  data: JSON.stringify({
                    file1Array: file1Array,
                    file2Array: file2Array,
                    file3Array: file3Array,
                    mainResponse: response.images[0],
                  }),
                  success: function (data) {
                    if (data.redirect_url) {
                        if (data.message) {
                            alert(data.message); 
                        }
                        window.location.href = data.redirect_url;  // Redirect to the specified URL
                    } else {
                        if (data.message) {
                            alert(data.message); 
                            window.location.href = '/auth/facial_recognition/';
                        }
                        console.log(data); 
                    }
                  },
                  error: function (xhr, status, error) {
                    // Handle errors
                    console.error(xhr.responseText);
                  },
                });

                // Now you have file1Array and file2Array
                // You can proceed to retrieve the third array from the database
                // Once you have all three arrays, you can combine them to form the original image
                // Example: var combinedArray = file1Array.concat(file2Array, thirdArray);
              };
              reader3.readAsText(file3);
            };

            reader2.readAsText(file2);
          };

          reader1.readAsText(file1);
        });
    }

    else {
      $.ajax({
        type: "POST",
        url: "../classify_face/",  // Replace with the correct URL mapping for your view
        data: {
          response: response.images[0],
        },  // You can pass any necessary data to the view
        success: function (data) {
            if (data.message) {
                alert(data.message);
            }
            // You can handle the response data as needed
            console.log(data);
        },
        error: function (xhr, status, error) {
            // Handle errors
            console.error(xhr.responseText);
        },
    });
    }

    // else {
    //   // else, the user is a first time user, i want to split the image and send him c1, c2, and r3
    //   // i want to send the image to the server
    //   // and get the shares
    //   // and then send the shares to the server
    //   // and then get the response from the server
    //   // and then redirect to the next page

    //   //get me the image of the user
    //   var image = document.getElementById('img-element');
    //   console.log("FROM LOGIN JS" + image);

    //   const response = event.detail.data.response;
    //   var reader = new FileReader();
    //   reader.onload = function (event) {
    //     var fileContent = event.target.result;
    //     var fileArray = fileContent.split(" ").map(Number); // Assuming each line contains a number

    //     $.ajax({
    //       type: "POST",
    //       url: "../split_image/",
    //       data: JSON.stringify({ fileArray: fileArray }),
    //       success: function (data) {
    //         if (data.redirect_url) {
    //           window.location.href = data.redirect_url;  // Redirect to the specified URL
    //         } else {
    //           console.log(data); 
    //         }
    //       },
    //       error: function (xhr, status, error) {
    //         // Handle errors
    //         console.error(xhr.responseText);
    //       },
    //     });
    //   };
    // }
    

 



    // $.ajax({
    //   type: "POST",
    //   url: "../facial_recognition/verify/",
    //   data: { response: response.images[0] }, // Assuming response.body contains the data to send
    //   success: function (data) {
    //     // Handle the success response from the server
    //     console.log(data);
    //   },
    //   error: function (xhr, status, error) {
    //     // Handle errors
    //     console.error(xhr.responseText);
    //   },
    // });
  }
}

component.addEventListener("face-liveness", listener);

// const csrftoken = getCookie('csrftoken');

// const video = document.getElementById('video-element');
// const image = document.getElementById('img-element');
// const captureBtn = document.getElementById('capture-btn');
// const reloadBtn = document.getElementById('reload-btn');

// reloadBtn.addEventListener('click', function() {
//     window.location.reload();
// });

// if(navigator.mediaDevices.getUserMedia) {
//     navigator.mediaDevices.getUserMedia({video: true})
//     .then(function(stream) {
//         video.srcObject = stream;
//         const { width, height } = stream.getTracks()[0].getSettings();
//         captureBtn.addEventListener('click', function() {
//             captureBtn.style.display = 'none';
//             const track = stream.getVideoTracks()[0];
//             const imageCapture = new ImageCapture(track);
//             console.log(imageCapture);
//             imageCapture.takePhoto().then((blob) => {
//                     // image.src = URL.createObjectURL(blob);
//                     // image.style.display = 'block';
//                     // track.stop();

//                     const img  = new Image(width,height);
//                     img.src = URL.createObjectURL(blob);
//                     image.append(img);
//                     video.style.display = 'none';
//                     console.log("took photo", blob);

//                     const reader = new FileReader();
//                     reader.readAsDataURL(blob);
//                     reader.onloadend = function() {
//                         const base64data = reader.result;
//                         console.log(base64data);

//                         const fd = new FormData();
//                         fd.append('csrfmiddlewaretoken', csrftoken);
//                         fd.append('photo', base64data);

//                         $.ajax({
//                             type: 'POST',
//                             url: 'classify/',
//                             enctype: 'multipart/form-data',
//                             data: JSON.stringify({ photo: base64data, csrfmiddlewaretoken: csrftoken }),
//                             processData: false,
//                             contentType: false,

//                             success: (resp) => {
//                                 console.log(resp);
//                                 // print(success)
//                                 if (resp.success){
//                                     // window.location.href = window.location.origin;
//                                     window.location.href = window.location.origin;
//                                 }
//                                 else{
//                                     alert(resp.message)
//                                     if (resp.message == 'Maximum attempts reached. Session ended.'){
//                                         window.location.href = '/';
//                                     }
//                                     else{
//                                         window.location.href = '/auth/facial_recognition/';
//                                     }
//                                 }
//                                 // window.location.href = '/helios_auth/login/'
//                             },
//                             error: (err) => {
//                                 console.log(err);
//                             },
//                         })

//                     }
//                 }
//             )
//     });
// });
// }

// get the  result of face-c

// window.location.href = window.location.origin;

// $.ajax({
//     type: 'POST',
//     url: 'classify/',
//     enctype: 'multipart/form-data',
//     data: JSON.stringify({ photo: response.images[0] }),
//     processData: false,
//     contentType: false,

//     // success: () => {
//     //     console.log(resp);
//     //     // print(success)
//     //     if (resp.success){
//     //         // window.location.href = window.location.origin;
//     //         window.location.href = window.location.origin;
//     //     }
//     // }
// })

//     else{
//         alert(resp.message)
//         if (resp.message == 'Maximum attempts reached. Session ended.'){
//             window.location.href = '/';
//         }
//         else{
//             window.location.href = '/auth/facial_recognition/';
//         }
//     }
//     // window.location.href = '/helios_auth/login/'
// },
// error: (err) => {
//     console.log(err);
// },
// }
