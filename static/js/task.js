/*
 * Requires:
 *     psiturk.js
 *     utils.js
 */

// Initalize psiturk object
var psiTurk = new PsiTurk(uniqueId, adServerLoc);

var mycondition = condition;  // these two variables are passed by the psiturk server process
var mycounterbalance = counterbalance;  // they tell you which condition you have been assigned to
// they are not used in the stroop code but may be useful to you

// All pages to be loaded
var pages = [
	"instructions/instruct-1.html",
	"instructions/instruct-2.html",
	"instructions/instruct-3.html",
	"instructions/instruct-ready.html",
	"stage.html",
	"postquestionnaire.html"
];

psiTurk.preloadPages(pages);

var instructionPages = [ // add as a list as many pages as you like
	"instructions/instruct-1.html",
	"instructions/instruct-2.html",
	//"instructions/instruct-3.html",
	//"instructions/instruct-ready.html"
];


/********************
* HTML manipulation
*
* All HTML files in the templates directory are requested 
* from the server when the PsiTurk object is created above. We
* need code to get those pages from the PsiTurk object and 
* insert them into the document.
*
********************/

/********************
* STROOP TEST       *
********************/

var StroopExperiment = function(targetR,startingDis,mode) {

	var wordon, // time word is presented
	    listening = false;

	// Stimuli for a basic Stroop experiment
	
	var MODE = "Above"; // task mode: the variable r is above or below the target.

	var variableR = (MODE=="Above")? targetR+startingDis: targetR- startingDis;
	var answer = "Left";
	var iniTrials = 24;
	var totalTrial = 50;
	var totalTrialsLeft = totalTrial;
	var windows=[];

	var next = function() {
		if (totalTrialsLeft<=0) {
			finish();
		} else if((windows.length == iniTrials)&&(check_convergnece(windows))) {
			finish();
		} else {
			//randomize answer
			answer = (Math.random()>0.5)?"Left":"Right"
			
			$("#stim").hide();
			$("#loading").show();
  
     		$("#trialNum").html("Trial Number "+String(totalTrial - totalTrialsLeft+1 +" (The total number of trials ranges from 24 to 50)."));

			show_fig(targetR,variableR,answer);
			
			wordon = new Date().getTime();
			listening = true;
			d3.select("#query").html('<h3 id="prompt">Press "L" or the left arrow <span class="glyphicon glyphicon-arrow-left"></span> for the left figure.<br> Press"R" or the right arrow <span class="glyphicon glyphicon-arrow-right"></span> for the right figure.</h3>');
		}
	};
	
	var response_handler = function(e) {
		if (!listening) return;

		var keyCode = e.keyCode,
			response;

		switch (keyCode) {
			case 37:// left arrow
				response="Left";
				break;
			case 39:
				response="Right";
				break;
			case 76:
				// "L"
				response="Left";
				break;
			case 82:
				// "R"
				response="Right";
				break;
		
			default:
				response = "";
				break;
		}
		if (response.length>0) {
			listening = false;
			var hit = response == answer;
			var rt = new Date().getTime() - wordon;
			var distance = Math.abs(variableR-targetR)
			//maintain the sliding window of the last 24 numbers. 
			windows.push(distance);
			if (windows.length>iniTrials) {windows.shift();}
			
			psiTurk.recordTrialData({'phase':"TEST",
                                     'targetR':targetR,
                                     'variableR':variableR,
                                     'answer':answer,
                                     'response':response,
                                     'hit':hit,
                                     'rt':rt}
                                   );

			//adapt the distance for the next run based on previous answers
			if (MODE=="Above"){variableR = hit? variableR-0.01 :variableR+0.03; if(variableR<=targetR){variableR = targetR +0.01}}
			else if (MODE=="Below"){variableR = hit? variableR+0.01 :variableR-0.03; if(variableR>=targetR){variableR = targetR -0.01}};
			variableR = (variableR>1)? 1:variableR;
			variableR = (variableR<0)? 0:variableR;

			totalTrialsLeft -=1;


			remove_word();
			next();
		}
	};

	var finish = function() {
	    $("body").unbind("keydown", response_handler); // Unbind keys
	    currentview = new Questionnaire();
	};
	
	var check_convergnece = function(windows){
		console.assert(windows.length == iniTrials, "wrong window size");
			var return_val = false
			$.ajax({
		    type: "POST",
		    async:false,

		    contentType: "application/json; charset=utf-8",
		    url: "/check_window",
		    data: JSON.stringify(windows),
		    success: function (data) {     
		    	data = JSON.parse(data);
		    	console.log(data);

		   		if (data["status"]=='OK'){ console.log("OK"); return_val= true;}
		   	},
		 	});
		return return_val;
	}

	var show_fig = function(targetR, variableR,answer) {
	LowerR = (MODE=="Below")? variableR:targetR
	HigherR= (MODE=="Above")? variableR:targetR
	//assign the figure r according to the answer.
	var qu = (answer=="Left")? {"r1":HigherR,"r2":LowerR}:{"r2":HigherR,"r1":LowerR}

  	$.ajax({
    type: "POST",
    async:true,
    contentType: "application/json; charset=utf-8",
    url: "/query",
    data: JSON.stringify(qu),
    success: function (data) {     
     var graph = $("#stim");
     graph.html(data);  
     $("#loading").hide(); 
     $("#stim").show();
   	},
   	dataType: "html"
 	});

	};

	var remove_word = function() {
		d3.select("#word").remove();
	};

	
	// Load the stage.html snippet into the body of the page
	psiTurk.showPage('stage.html');

	// Register the response handler that is defined above to handle any
	// key down events.
	$("body").focus().keydown(response_handler); 

	// Start the test
	next();
};


/****************
* Questionnaire *
****************/

var Questionnaire = function() {

	var error_message = "<h1>Oops!</h1><p>Something went wrong submitting your HIT. This might happen if you lose your internet connection. Press the button to resubmit.</p><button id='resubmit'>Resubmit</button>";

	record_responses = function() {

		psiTurk.recordTrialData({'phase':'postquestionnaire', 'status':'submit'});

		$('textarea').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);
		});
		$('select').each( function(i, val) {
			psiTurk.recordUnstructuredData(this.id, this.value);		
		});

	};

	prompt_resubmit = function() {
		document.body.innerHTML = error_message;
		$("#resubmit").click(resubmit);
	};

	resubmit = function() {
		document.body.innerHTML = "<h1>Trying to resubmit...</h1>";
		reprompt = setTimeout(prompt_resubmit, 10000);
		
		psiTurk.saveData({
			success: function() {
			    clearInterval(reprompt); 
                psiTurk.computeBonus('compute_bonus', function(){finish()}); 
			}, 
			error: prompt_resubmit
		});
	};

	// Load the questionnaire snippet 
	psiTurk.showPage('postquestionnaire.html');
	psiTurk.recordTrialData({'phase':'postquestionnaire', 'status':'begin'});
	
	$("#next").click(function () {
	    record_responses();
	    psiTurk.saveData({
            success: function(){
                psiTurk.computeBonus('compute_bonus', function() { 
                	psiTurk.completeHIT(); // when finished saving compute bonus, the quit
                }); 
            }, 
            error: prompt_resubmit});
	});
    
	
};

// Task object to keep track of the current phase
var currentview;

/*******************
 * Run Task
 ******************/
$(window).load( function(){
    psiTurk.doInstructions(
    	instructionPages, // a list of pages you want to display in sequence
    	function() { currentview = new StroopExperiment(0.9,0.10,"Above"); } // what you want to do when you are done with instructions
    );
});
