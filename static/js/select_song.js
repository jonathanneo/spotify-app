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
    $.get("/api/select_top_song", () => {
        setTimeout(currently_playing, 2000); // wait for 2000 ms
    });
});

currently_playing();
