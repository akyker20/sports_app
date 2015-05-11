$(document).ready(function(){

	$('div.heading h1.header').on("click", "span.not-watching", function(){
		$.ajax({
			url: "/athletes/watch_player/" + $(this).data('athlete-id'),
			type: "POST",
		}).success(swapWatchOptions);
	});

	$('div.heading h1.header').on("click", "span.watching", function(){
		$.ajax({
			url: "/athletes/unwatch_player/" + $(this).data('athlete-id'),
			type: "POST",
		}).success(swapWatchOptions);
	});

	function swapWatchOptions(html) {
		$('div.heading h1.header span').remove();
		$('div.heading h1.header').append(html);
	}
});

