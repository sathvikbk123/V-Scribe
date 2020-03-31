$(document).ready(function(){
  $("*").click(function(event){
    event.stopPropagation();
    /*var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    var recognition = new SpeechRecognition();
    recognition.start();
    recognition.onstart = function(){
      console.log("started");
    }
    recognition.onspeechend = function(){
      console.log("ended");
    }
    recognition.onerror = function(event){
      if(event.error == 'no-speech'){
        console.log("try again");
      }
    }
    recognition.onresult = function(event) {

  // event is a SpeechRecognitionEvent object.
  // It holds all the lines we have captured so far.
  // We only need the current one.
      var current = event.resultIndex;

  // Get a transcript of what was said.
      var transcript = event.results[current][0].transcript;

  // Add the current transcript to the contents of our Note.
      console.log(transcript);
      console.log('in it')
      console.log("calling ajax")*/
      //console.log($("#option1").is(':checked'))
      $.ajax({
          data : {
            //text : transcript,
            dummy:"verification"
          },
          type:'POST',
          url : '/verify'
      }).done(function(data){
          console.log("ajax done")
          if(data.res==="1"){
            window.location.href="/"
          }
          else{
            window.location.href="/error"
          }

      })
    //}

  });
});
