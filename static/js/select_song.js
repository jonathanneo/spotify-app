let song_img = $("#song_img");
let song_name = $("#song_name");
let song_album_artist = $("#song_album_artist");
let spinner = $("#spinner");
let song_content = $("#song_content");
let button = $("#surprise_me");

function currently_playing() {
    $.get("/api/currently_playing", (data) => {
        if (data.is_playing) {
            song_img.attr("src", data.item.album.images[0].url);
            song_name.text(data.item.name);
            song_album_artist.text(`${data.item.album.name}, ${data.item.artists[0].name}`);
        } else {
            song_name.text("No song playing");
        }
        button.html("Surprise me");
    });
}


button.click(() => {
    button.html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`)
    $.get("/api/devices", (activeDevices) => {
        // if there is an active device 
        if (activeDevices.devices.length > 0) {
            // get the top song 
            $.get("/api/select_top_song", (data) => {
                song_img.attr("src", data.album.images[0].url);
                song_name.text(data.name);
                song_album_artist.text(`${data.album.name}, ${data.artists[0].name}`);
                button.html("Surprise me");
            });
        } else {
            song_img.removeAttr("src");
            song_name.text("No active device");
            song_album_artist.text("Open spotify player and play a song.");
            button.html("Surprise me");
        }
    })

});

currently_playing();
