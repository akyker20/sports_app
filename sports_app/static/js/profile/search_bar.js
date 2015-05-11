$(document).ready(function(){
	$('div.heading span.glyphicon-search').click(function(e){
		$('div.heading div.search-and-results').toggleClass('hidden');
		e.stopPropagation();
	});

	$(document).click(function() {
    	$('div.heading div.search-and-results').addClass('hidden');
	});

	$("div.heading div.search-and-results").click(function(e) {
	    e.stopPropagation(); // This is the preferred method.
	});

	$('div.heading input').keydown(function(e){
		var inputVal = $(this).val();
		if(e.keyCode === 32) {
			$.ajax({
				url: "/athletes/search/",
				type: "GET",
				data: {"search":inputVal},
			}).success(function(html){
				clearSearchList();
				$('div.heading div.search-and-results').append(html);
			});
		}
		// If key pressed was backspace or escape
		if(e.keyCode === 8 && inputVal.length <= 1 || e.keyCode == 27) {
			clearSearchList();
		}
	});

	function clearSearchList() {
		$('div.heading div.search-and-results ul.search-results').remove();
	}
});