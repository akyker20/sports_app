$(document).ready(function(){

	var dashMediaPlayer, 
      currentVideo,
      clipTimer,
      current_mpd_url;

  var playable_clips = [];
  var current_clip_index = 0;

  var athlete_watching = [];

  function Clip(start, end) {
    this.start_time = start;
    this.end_time = end;
  }

  if($(".gridster ul").length) {
      var gridster = $(".gridster ul").gridster({
      widget_margins: [10, 10],
      widget_base_dimensions: [130, 130],
      // resize.enabled: false
    }).data('gridster');

    if(gridster) {
      gridster.$widgets.click(playRegularVideo);
    }
  }


	$('div.cc-right-container textarea').keydown(comment);

	$('section.video-modal').on("click", 'div.video-modal button.star', star);
	$('section.video-modal').on("click", "div.replay-clip", replayClip);
  $('section.video-modal').on("keydown", 'div.cc-right-container textarea', comment);
  $("section.video-modal").on("click", "div.video-modal span.modal-close", removeVideoModal);
  $('section.video-modal').on("click", "div#gamestat-submodal-clips img.weak", playGamestatVideo);


  $('section.video-modal').on("click", "button#game-comments", showGameComments);
  $('section.video-modal').on("click", "button#game-gamestats", showGameGamestats);

  // $('section.video-modal').on("keydown", "gamefilm-tag-container")

  
  function showGameComments() {
    $('section.video-modal div.game-gamestats-container').fadeOut(function(){
      $('section.video-modal div.cc-right-container').fadeIn();
    });
  }

  function showGameGamestats() {
    $('section.video-modal div.cc-right-container').fadeOut(function(){
      $('section.video-modal div.game-gamestats-container').fadeIn();
    });
  }


  $('div.gamestat-block').click(gamestatClicked);
  $('section.video-modal').on("click", "ul li.player-stat-container.gamestat-selectable", gamestatClicked);

  function gamestatClicked() {
    var id = $(this).data('id');
    $.ajax({
      url: "/athletes/get_gamestat",
        type: "GET",
        data: { 'stat_id':id },
    }).success(function(json) {

      resetPlayableClips();

      addBackgroundOpacity();

      $('section.video-modal').html(json['html']);

      if('dash_info' in json) {
        var start_time = parseFloat(json['dash_info']['start_time']);
        var end_time = parseFloat(json['dash_info']['end_time']);
        current_mpd_url = json['dash_info']['mpd_url'];
        playable_clips.push(new Clip(start_time, end_time));
        playGameFilmClip();
      }

      // fillAllVisibleGamestats($('div#gamestat-submodal-progress div.progress.stats'));
      $('section.video-modal div#gamestat-submodal-clips img').first().removeClass('weak');
    });

  }

  $("section").not('.video-modal').click(removeVideoModal);

	$('button.star').click(star);

  $('section.video-modal').on("click", "button#gamestat-view-game", displayGameModal);
  $("a.view-game").click(displayGameModal);


  $('section.top10 ul li img.img-selectable').click(playRegularVideo);

  function playRegularVideo() {
    var clip_id = $(this).data('clip-id');
    var elementToInsertVideo = $('section.video-modal');
    playVideo(elementToInsertVideo, clip_id);
  }

  function playGamestatVideo() {
    var clip_id = $(this).data('clip-id');
    var elementToInsertVideo = $('section.video-modal div#cc-container');
    playVideo(elementToInsertVideo, clip_id);

    $('section.video-modal img').not('weak').addClass('weak');
    $(this).removeClass('weak');
  }

  function playVideo(elementToInsertVideo, clip_id) {

    $.ajax({
      url: "/athletes/play_clip",
      type: "GET",
      data: { 'clip_id':clip_id },
    }).success(function(json){
      
      resetPlayableClips();

      addBackgroundOpacity();

      elementToInsertVideo.html(json['html']);
      
      if('dash_info' in json) {
        var start_time = parseFloat(json['dash_info']['start_time']);
        var end_time = parseFloat(json['dash_info']['end_time']);
        current_mpd_url = json['dash_info']['mpd_url'];
        playable_clips.push(new Clip(start_time, end_time));
        playGameFilmClip();
      }
    });
    
  }

  function addBackgroundOpacity() {
    $('section').not('section.video-modal').addClass('opaque');
  }

  function removeBackgroundOpacity() {
    $("section").not('section.video-modal').removeClass('opaque');
  }

  function removeVideoModal() {
    if(currentVideo) {
      currentVideo.pause();
      resetPlayableClips();
    }

    removeBackgroundOpacity();

    var childrenToDelete = $("section.video-modal").children();
    childrenToDelete.fadeOut(function(){
      childrenToDelete.remove();
    });
  }

  function replayClip() {
    $(currentVideo).parent().find('div.replay-clip').fadeOut(function() {
    	playDashClip();
    });
  }

	function displayGameModal() {
		var game_id = $(this).data('game-id');
		$.ajax({
			url: "/athletes/show_game",
			type: "GET",
			data: {"game_id": game_id },
		}).success(function(json){

			removeVideoModal();
      resetPlayableClips();
      addBackgroundOpacity();

			$('section.video-modal').html(json['html']);

      var time_ranges = json['dash_info']['highlights_time_ranges'];
      current_mpd_url = json['dash_info']['mpd_url'];
      for (i in time_ranges) {
        playable_clips.push(new Clip(time_ranges[i]['start_time'], 
                                     time_ranges[i]['end_time']));
      }

			if(playable_clips.length > 0) {
				playGameFilmClip();
			}

      // fillAllVisibleGamestats($('section.video-modal div.progress.stats'));

		});
	}

	function star(e) {
		e.stopPropagation();
		var starBtn = $(this);
		var parent = starBtn.parent();
		var starType = parent.data('type');
		var id = parent.data('id');
		$.ajax({
			url: "/athletes/star/",
			type: "POST",
			data: {"type":starType,"id": id },
		}).success(function(html){
			starBtn.remove();
			parent.append(html);
		});
	}

	function comment(e){
		var input = $(this);
		var commentType = input.data('type');
		var inputVal = $(this).val();
		var id = input.data('id');
		var commentsList = input.parent().find('ul.comments');
		if(e.keyCode === 13 && inputVal) {
			$.ajax({
				url: "/athletes/comment/",
				type: "POST",
				data: {"content":inputVal, "type":commentType,"id": id },
			}).success(function(html){
				commentsList.append(html);
				input.val('');
			});
		}
	}

	$('li#notifications').click(function(){
		$(this).parent().find('ul#notification-list').slideToggle();
	});

	$('ul#notification-list li').click(function(){
    var notification = $(this);
		var gamefilm_id = notification.data('gamefilm-id');
    var notification_id = notification.data('notification-id');
    loadGamefilmModal({"gamefilm-id": gamefilm_id, "notification-id": notification_id });
    notification.fadeOut();
	});

  $("a.view-gamefilm").click(function(){
    var gamefilm_id = $(this).data('gamefilm-id');
    loadGamefilmModal({"gamefilm-id": gamefilm_id});
  });


  function loadGamefilmModal(data) {
    $.ajax({
      url: "/athletes/play_gamefilm",
      type: "GET",
      data: data
    }).success(function(json){
      resetPlayableClips();
      addBackgroundOpacity();
      athlete_watching = json['watching'];
      $('section.video-modal').html(json['html']);
      current_mpd_url = $('div.video-modal').data('mpd-url');
      playDashContent();
      $('div.video-modal video')[0].autoplay = true;
    });
  }

  function resetPlayableClips() {
    current_clip_index = 0;
    playable_clips.length = 0;
    current_mpd_url = null;
    currentVideo = null;
  }

	function playDashContent() {
		var context = new Dash.di.DashContext();
	  dashMediaPlayer = new MediaPlayer(context);
	  currentVideo = document.querySelector("#movie");
	  dashMediaPlayer.startup();
	  dashMediaPlayer.attachView(currentVideo);
	  dashMediaPlayer.attachSource(current_mpd_url);
	  currentVideo.autoplay = true;
  }

  function playGameFilmClip(){
    playDashContent();
    currentVideo.controls = false;
    currentVideo.pause();
    setTimeout(function() {
    	playDashClip();
    }, 1000);
  }

    function playDashClip() {
      dashMediaPlayer.seek(playable_clips[current_clip_index].start_time);
      currentVideo.play();
      clipTimer = setInterval(function(){
        if(currentVideo.currentTime > playable_clips[current_clip_index].end_time) {
          currentVideo.pause();
          clearInterval(clipTimer);
        	tryToPlayNextClip();
        }
      }, 1000);
    }

    function tryToPlayNextClip() {
    	if(current_clip_index < playable_clips.length - 1) {
    		current_clip_index++;
    		playDashClip();
    	} else {
        current_clip_index = 0;
        $(currentVideo).parent().find('div.replay-clip').fadeIn();
      }
    }


  //GAMESTATS JS

  const MIN_STAT_BAR_WIDTH = 5;

  const statWeights = {
    'points': 2,
    'assists': 3,
    'blocks': 3,
    'rebounds': 2,
    'steals': 3,
  }

  const shorterNames = {
    'points':'pts',
    'rebounds': 'reb',
    'assists': 'asts',
    'blocks': 'blk',
    'steals': 'stls',
  }


  fillAllVisibleGamestats($('div.progress.stats'));

  function fillAllVisibleGamestats(gamestats) {
    gamestats.each(function( index ) {
      fillGamestat(this);
    });
  }

  function fillGamestat(gamestatBar) {
      var rebounds =  $(gamestatBar).find('div#rebounds').data('rebounds');
      var blocks   =  $(gamestatBar).find('div#blocks').data('blocks');
      var steals   =  $(gamestatBar).find('div#steals').data('steals');
      var assists  =  $(gamestatBar).find('div#assists').data('assists');
      var points   =  $(gamestatBar).find('div#points').data('points');
      var params   =  [rebounds, blocks, steals, assists, points];

      $(gamestatBar).find('div.progress-bar').each( function( i ) {
        var progressBar = $(this)[0];
        
        var expanderTimer = setInterval(function(){

            var width = progressBar.style["width"];

            var myRe = /(\d+)%/;
            var width_number = parseInt(myRe.exec(width)[1]);
            if(params[i] > 0 || width_number < MIN_STAT_BAR_WIDTH) {
              temp_stat = progressBar.id;
              width_number += statWeights[temp_stat];
              progressBar.style["width"] = width_number + "%";
              params[i] -= 1;
              $(progressBar).text((width_number/statWeights[temp_stat]).toString() + " " + shorterNames[temp_stat]);
              return;
            }

            clearInterval(expanderTimer);

        }, 200);
      });
  }

  // TEAM JS

  $('section.team-heading div.team-options ul.nav li').click(function(){
    var previouslyActiveLI = $('section.team-heading div.team-options ul.nav li.active');
    var clickedLI = $(this);

    if(!clickedLI.hasClass("active")) {
      var divStr = "section.team-payload div.";

      $(divStr + previouslyActiveLI.data('id')).fadeOut(function() {
        $(divStr + clickedLI.data('id')).fadeIn();

      });

      previouslyActiveLI.removeClass("active");
      clickedLI.addClass("active");
    }

  });







  //END GAMESTATS JS
});