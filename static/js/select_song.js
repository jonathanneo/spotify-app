
console.log("Hello");
let song_img = $("#song_img");
let song_name = $("#song_name");
let song_album_artist = $("#song_album_artist");

function currently_playing() {
    $.get("/api/currently_playing", (data) => {
        if (data.is_playing) {
            song_img.attr("src", data.item.album.images[0].url);
            song_name.text(data.item.name);
            song_album_artist.text(`${data.item.album.name}, ${data.item.artists[0].name}`);
        } else {
            song_name.text("No song playing");
        }
    });
}

currently_playing();

$("#surprise_me").click(() => {
    $.get("/api/select_top_song", (data) => {
        currently_playing();
    });
});