export function initCopyComment(container) {
    container.addEventListener("click", e => {
        const btn = e.target.closest("[data-copy-comment]");
        if (!btn) return;

        const commentId = btn.dataset.copyComment;
        const text = container
            .querySelector(`[data-comment-id="${commentId}"] .comment-text`)
            ?.textContent
            ?.trim();

        if (!text) return;

        navigator.clipboard.writeText(text);
    });
}
