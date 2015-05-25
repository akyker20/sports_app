$(document).ready(function(){

	const BUFFERED_CONTROL_WIDTH = 518;
	const BUFFERED_CONTROL_RIGHT_OFFSET = 68;
	const TIMER_SPEED = 200;

	var regex = /(\w+).*px/;

	var clip_start_time, clip_end_time, clip_timer;
	var video, clip_bar, video_modal;
	var gamefilm_file_size;
	var clip_creation_in_progress = false;
	var selected_clip_id;

	$('section.video-modal').on("click", 'div.clip-bar', handle_clip_bar_click);
	$('section.video-modal').on("click", 'div.create-clip', start_clip_creation);
	$('section.video-modal').on("click", 'div.cancel-clip-creation', end_clip_creation);
	$('section.video-modal').on("click", 'div.save-clip-creation', begin_tag_process);
	$('section.video-modal').on("click", 'div.delete-clip', delete_clip);
	$('section.video-modal').on("click", 'div.edit-clip', edit_clip);
	$('section.video-modal').on("click", 'div.save-clip-edit', save_clip_edit);
	$('section.video-modal').on("click", 'div.revert-clip', revert_clip);
	$('section.video-modal').on("keyup", "div.gamefilm-tag-container input", searchTaggablePlayers);
	$('section.video-modal').on("click", "div.gamefilm-tag-container img", save_clip);
	$('section.video-modal').on("click", "div.gamefilm-tag-container ul li", save_clip);



	function searchTaggablePlayers(){
	    
	    var inputVal = $(this).val().toLowerCase();
	    if(inputVal) {
	      $('div.gamefilm-tag-container li').each(function( index ){
	        var playerName = $(this).text().toLowerCase();
	        if(!$(this).is(":visible") && playerName.indexOf(inputVal) > -1) {
	          $(this).show();
	        }
	        else if($(this).is(":visible") && playerName.indexOf(inputVal) === -1) {
	          $(this).hide();
	        }
	      });

	      if($('div.gamefilm-tag-container img').is(':visible')) {
	        $('div.gamefilm-tag-container img').addClass('weak');
	      }

	    } else {
	      $('div.gamefilm-tag-container li:visible').hide(); 
	      $('div.gamefilm-tag-container img').removeClass('weak');
	    }
	}


	function edit_clip() {

		video = $('div.video-modal video')[0];

		var width_pixels = parseInt(regex.exec(clip_bar.css('width'))[1]);
		var left_pixels = parseInt(regex.exec(clip_bar.css('left'))[1]);
		clip_start_time = ((left_pixels - BUFFERED_CONTROL_RIGHT_OFFSET)/BUFFERED_CONTROL_WIDTH)*video.duration;
		var end_time = clip_start_time + (width_pixels/BUFFERED_CONTROL_WIDTH)*video.duration;

		clip_creation_in_progress = true;

		video.play();
		video.currentTime = end_time;
		video.pause();
		start_clip_creation_timer();

		hide_all_options();
		$('div.save-clip-edit').fadeIn();
		$('div.revert-clip').fadeIn();

	}

	function revert_clip() {
		clip_bar.fadeOut();
		hide_all_options();
		$('div.create-clip').fadeIn();
		$('div.clip-bar:hidden').fadeIn();
	}


	function begin_tag_process() {
		if(clip_creation_in_progress){
			video.pause();
			clip_end_time = video.currentTime;
			var duration = clip_end_time - clip_start_time;
			
			if(duration < 3) {
				alert("Clips must be at least 3 seconds in duration");
			} else if (duration > 30) {
				alert("Clips must be less than 30 seconds in duration.");
			} else {
				$('div.gamefilm-tag-container').fadeIn();
			}
		}
	}


	function save_clip_edit() {
		hide_all_options();
		$('div.create-clip').fadeIn();
		video_modal = $('div.video-modal');
		video = $('div.video-modal video')[0];
		clip_end_time = video.currentTime;
		var clip_id = $('div.clip-bar:hidden').data('clip-id');
		
		$.ajax({
			url: "/athletes/update_gamefilm_clip",
			type: "POST",
			data: { "clip_id":clip_id, "start_time": clip_start_time, "end_time": clip_end_time }
		}).success(function(html) {
			$('div.clip_bar').remove();
			video_modal.prepend(html);
			end_clip_creation();
		});
	}


	function delete_clip() {
		if(selected_clip_id) {
			$.ajax({
				url: "/athletes/delete_gamefilm_clip",
				type: "POST",
				data: { "clip_id":selected_clip_id }
			}).success(function() {
				clip_bar.fadeOut();
				$('div.clip-bar:hidden').remove();
				hide_all_options();
				$('div.create-clip').fadeIn();
			});
		}
	}

	//When a clip is selected, the green click bar disappears and is
	//replaced by the orange creation bar div that assumes its width
	//and position.
	function handle_clip_bar_click() {
		if(!clip_creation_in_progress) {
			$('div.clip-bar:hidden').show();
			hide_all_options();
			$('div.edit-clip').fadeIn();
			$('div.delete-clip').fadeIn();
			selected_clip_id = $(this).data('clip-id')
			clip_bar = $('div#clip-creation-bar');
			clip_bar.css('width', $(this).css('width'));
			clip_bar.css('left', $(this).css('left'));
			clip_bar.fadeIn();
			$(this).hide();
		}
	}

	function hide_all_options() {
		$('div.cancel-clip-creation').fadeOut();
		$('div.save-clip-creation').fadeOut();
		$('div.create-clip').fadeOut();
		$('div.edit-clip').fadeOut();
		$('div.delete-clip').fadeOut();
		$('div.save-clip-edit').fadeOut();
		$('div.revert-clip').fadeOut();
	}

	//After validating the clip is a valid length (between 3 and 30 sec in duration),
	//an ajax request is sent to the server to create a new GameFilmClip model with
	//the appropriate start and end times.
	function save_clip() {
		var athleteID = $(this).data('athlete-id');
		var gamefilm_id = video_modal.data('gamefilm-id');

		$.ajax({
			url: "/athletes/create_gamefilmclip",
			type: "POST",
			data: {"gamefilm_id": gamefilm_id, "start_time": clip_start_time, "end_time": clip_end_time,
				  "athlete_id": athleteID }
		}).success(function(html) {
			$('div.clip_bar').remove();
			video_modal.prepend(html);
			end_clip_creation();
			$('div.gamefilm-tag-container').fadeOut();
			$('div.gamefilm-tag-container img').removeClass('weak');
			$('div.gamefilm-tag-container input').text("");
			$('div.gamefilm-tag-container ul li').hide();
		});
			
		
	}


	//The purpose of this function is to initialize clip creation.
	//An orange bar becomes noticeable representing the time frame of the
	//clip that is being created.
	function start_clip_creation() {
		if(!clip_creation_in_progress){
			
			hide_all_options();
			$('div.save-clip-creation').fadeIn();
			$('div.cancel-clip-creation').fadeIn();

			clip_creation_in_progress = true;
			
			video_modal = $('div.video-modal');
			clip_bar = $('div#clip-creation-bar');
			clip_bar.css('width', '0px');
			clip_bar.fadeIn();
			video = $('div.video-modal video')[0];
			gamefilm_file_size = video_modal.data('file-size');
			clip_start_time = video.currentTime;
			var left_px = (video.currentTime/video.duration)*BUFFERED_CONTROL_WIDTH + BUFFERED_CONTROL_RIGHT_OFFSET;
			clip_bar.css('left', left_px + 'px');
			start_clip_creation_timer();
		}
	}

	function start_clip_creation_timer() {
		clip_timer = setInterval(function(){
			if(video.currentTime < clip_start_time) {
				end_clip_creation();
			}	
			else {
				var new_width = [(video.currentTime - clip_start_time)/video.duration]*BUFFERED_CONTROL_WIDTH;
				clip_bar.css('width', new_width + 'px');
			}
		}, TIMER_SPEED);
	}

	//Return to original state.
	function end_clip_creation() {
		clearInterval(clip_timer);
		clip_bar.css("width", '0px');
		clip_bar.fadeOut();
		clip_creation_in_progress = false;
		hide_all_options();
		$('div.create-clip').fadeIn();
	}

});