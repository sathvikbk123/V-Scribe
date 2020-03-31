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
            qno:$("#qno").text(),
            question:$("#question").text(),
            answer:$("#answer").val(),
            option1:$("#option1").text(),
            option2:$("#option2").text(),
          },
          type:'POST',
          url : '/speech'
      }).done(function(data){
          console.log("ajax done")
          $("#qno").text(data.qno);
          $("#question").text(data.question);
          $("#answer").html(data.answer).show();
          $("#option1").text(data.option1).hide();
          $("#option2").text(data.option2).hide();
          $("#checkop1").hide();
          $("#checkop2").hide();
          //$("#option1").prop("checked", true);
          if (data.qno === "3"){
            console.log("entered");
            if(data.answer === "option A"){
              $("#checkop1").prop("checked", true);
              $("#checkop2").prop("checked", false);
            }
            else if(data.answer === "option B"){
              console.log("here")
              $("#checkop2").prop("checked", true);
              $("#checkop1").prop("checked", false);
            }
            $("#question").text(data.question);
            $("#option1").text(data.option1).show();
            $("#option2").text(data.option2).show();
            $("#checkop1").show();
            $("#checkop2").show();
            $("#answer").hide();
        }
        if(data.qno === "end"){
          window.location.href = "/end"
        }

      })
    //}

  });
});
