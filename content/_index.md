---
# Striking header background image, Ideal images are homogenous around the centre and contrasting to the text. Non-ideal images can use `title_guard`
header_image: "images/background.png"
#
# When set true, uses video from custom_header_video.html partial, instead of header_image
header_use_video: false
#
# Optional header logo. CSS: `#blog-logo`, with max-height defined, optimize to prevent scaling
header_logo: "images/Second_Wind_Logo_White.png"
title: "Second Wind 2025"
#
# Headers are safeHTML, you can use HTML tags such as b,i,u,br
header_headline: "JULY 11-13 2025"
header_subheadline: "<p>Presented by <a target='_blank' href='https://respawn.co.nz/'>Respawn Esports Centre</a></p>

<script>
function updateTimer() {
  future  = new Date(1752211800 * 1000);
  now     = new Date();
  diff    = future - now;

  days  = Math.floor( diff / (1000*60*60*24) );
  hours = Math.floor( diff / (1000*60*60) );
  mins  = Math.floor( diff / (1000*60) );
  secs  = Math.floor( diff / 1000 );

  d = days;
  h = hours - days  * 24;
  m = mins  - hours * 60;
  s = secs  - mins  * 60;

  document.getElementById('timer')
    .innerHTML =
      d + '<span> days, </span>' +
      h + '<span> hours, </span>' +
      m + '<span> minutes, </span>' +
      s + '<span> seconds </span>' ;
}
setInterval('updateTimer()', 1000 );
</script>

<div style='font-size: 40px; background: black; padding: 15px; border-radius: 15px;' id='timer'></div>

<p><a class='btn site-menu' style='font-size: 32px; -webkit-border-radius: 6px; padding: 20px 30px; text-shadow: none;' href='https://www.start.gg/tournament/second-wind-2025/details' target='_blank' rel='noopener noreferrer'>Sign up now!</a></p>"


# Add a 'Go back to top' item to the navigation menu
# Title: name of navigation menu entry
# Weight (i. e. position in menu): none = no menu entry, first = add as first entry, last = ad as last entry
nav_to_top_title: "Return To Top"
nav_to_top_weight: last
---