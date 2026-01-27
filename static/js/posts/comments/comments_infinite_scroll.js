import { initInfiniteComments } from "./infinite.js";
import { initCommentLikes } from "./likes.js";
import { initCopyComment } from "./copy.js";
import { initCommentEdit } from "./edit.js";

document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("comments-box");
    if (!container) return;

    initInfiniteComments(container);
    initCommentLikes(container);
    initCopyComment(container);
    initCommentEdit();
});
