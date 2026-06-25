// Waits until the page content is fully loaded
document.addEventListener("DOMContentLoaded", function () {
    const gameMessage = document.querySelector(".game-message");
    const confirmButtons = document.querySelectorAll(".confirm-action");
    const modal = document.querySelector(".confirm-modal");
    const modalMessage = document.querySelector(".confirm-modal-message");
    const confirmButton = document.querySelector(".confirm-modal-confirm");
    const cancelButton = document.querySelector(".confirm-modal-cancel");
    const timerBars = document.querySelectorAll(".timer-bar");
    const page = document.body.dataset.page;
    const leaderboardList = document.querySelector("#leaderboard-list");

    let actionUrl = "";
    let shouldReload = false;

    if (gameMessage) {
        // Hides the temporary game message after a few seconds
        setTimeout(function () {
            gameMessage.classList.add("hide-message");
        }, 3000);

        // Reloads only the dashboard after the message disappears
        setTimeout(function () {
            if (page === "dashboard") {
                window.location.reload();
            }
        }, 3800);
    }

    // Opens the custom confirmation modal for important actions
    for (let i = 0; i < confirmButtons.length; i++) {
        confirmButtons[i].addEventListener("click", function (event) {
            event.preventDefault();

            actionUrl = confirmButtons[i].href;
            modalMessage.textContent = confirmButtons[i].dataset.confirmMessage;
            modal.classList.add("show-modal");
        });
    }

    if (confirmButton) {
        // Continues the selected action when the player confirms it
        confirmButton.addEventListener("click", function () {
            window.location.href = actionUrl;
        });
    }

    if (cancelButton) {
        // Closes the confirmation modal without doing the action
        cancelButton.addEventListener("click", function () {
            modal.classList.remove("show-modal");
            actionUrl = "";
        });
    }

    if (modal) {
        // Closes the modal when the player clicks outside the confirmation box
        modal.addEventListener("click", function (event) {
            if (event.target === modal) {
                modal.classList.remove("show-modal");
                actionUrl = "";
            }
        });
    }

    if (timerBars.length > 0) {
        // Updates all visible progress bars when the page opens
        updateProgressBars();

        // Keeps the progress bars moving smoothly while the page is open
        setInterval(function () {
            updateProgressBars();
        }, 50);
    }

    function updateProgressBars() {
        shouldReload = false;

        for (let i = 0; i < timerBars.length; i++) {
            const finishTimeText = timerBars[i].dataset.finishTime;
            const totalTime = Number(timerBars[i].dataset.totalTime);
            const fill = timerBars[i].querySelector(".progress-fill");
            const timerZone = timerBars[i].parentElement;
            const countdown = timerZone.querySelector(".timer-countdown");

            if (finishTimeText && totalTime > 0 && fill) {
                const finishTime = new Date(finishTimeText);
                const now = new Date();
                const remainingMilliseconds = finishTime - now;
                const totalMilliseconds = totalTime * 1000;

                let progress = 0;

                if (remainingMilliseconds <= 0) {
                    progress = 100;
                    shouldReload = true;

                    if (countdown) {
                        // Shows a short message when the timer is ending
                        countdown.textContent = "A terminar...";
                    }
                } else {
                    const remainingSeconds = Math.ceil(remainingMilliseconds / 1000);
                    progress = ((totalMilliseconds - remainingMilliseconds) / totalMilliseconds) * 100;

                    if (countdown) {
                        // Shows the remaining time above the progress bar
                        countdown.textContent = "Faltam " + remainingSeconds + "s";
                    }
                }

                if (progress < 0) {
                    progress = 0;
                }

                if (progress > 100) {
                    progress = 100;
                }

                // Updates only the green width of the progress bar
                fill.style.width = progress + "%";
            }
        }

        if (shouldReload && page === "dashboard") {
            reloadDashboardSafely();
        }
    }

    function reloadDashboardSafely() {
        if (modal && modal.classList.contains("show-modal")) {
            // Avoids refreshing the page while the confirmation modal is open
            return;
        }

        // Reloads the dashboard so Flask can update the real business state
        window.location.reload();
    }

    if (page === "leaderboard") {
    // Loads the leaderboard when the page opens
        loadLeaderboard();

        // Reloads leaderboard data every few seconds using Fetch API
        setInterval(function () {
            loadLeaderboard();
        }, 5000);
    }

    function loadLeaderboard() {
    if (!leaderboardList) {
        return;
    }

        // Requests leaderboard data from the Flask backend
        fetch("/api/leaderboard")
            .then(function (response) {
                return response.json();
            })
            .then(function (players) {
                leaderboardList.innerHTML = "";

                for (let i = 0; i < players.length; i++) {
                    const player = players[i];

                    const row = document.createElement("div");
                    row.classList.add("leaderboard-row");

                    if (player.position === 1) {
                        row.classList.add("first-place");
                    } else if (player.position === 2) {
                        row.classList.add("second-place");
                    } else if (player.position === 3) {
                        row.classList.add("third-place");
                    }

                    const position = document.createElement("strong");
                    position.textContent = player.position + "º";

                    const username = document.createElement("span");

                    // Shows the player username with rank icon and rank name
                    username.textContent = player.username + " - " + player.rank_icon + " " + player.rank_name;

                    const totalEarned = document.createElement("span");

                    // Shows the formatted total earned value with the euro symbol
                    totalEarned.textContent = formatValue(player.total_earned) + "€";

                    row.appendChild(position);
                    row.appendChild(username);
                    row.appendChild(totalEarned);

                    leaderboardList.appendChild(row);
                }
            });
        function formatValue(value) {
            // Formats large values in JavaScript for Fetch API results
            value = Number(value);

            if (value >= 1000000) {
                let formattedValue = Math.round((value / 1000000) * 100) / 100;
                return formattedValue.toString().replace(/\.?0+$/, "") + "M";
            }

            if (value >= 1000) {
                return (value / 1000).toFixed(1) + "k";
            }

            return value.toString();
        }
    }
});