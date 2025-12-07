

// =============================
// 게시판 목록 (무한 스크롤)
// =============================
let isPostDetailLoading = false;
let lastPostDetailId = null;  
let currentPostId = null; 

let boardState = {
  cursor: null,
  loading: false,
  done: false,
  posts: [],
};
console.log("board.js loaded");
async function loadPosts() {
  if (boardState.loading || boardState.done) return;
  boardState.loading = true;

  const loadingEl = document.getElementById("boardLoading");
  if (loadingEl) loadingEl.textContent = "불러오는 중...";

  try {
    const query = boardState.cursor
      ? `?cursor=${boardState.cursor}&limit=10`
      : "?limit=10";

    const res = await apiRequest("/posts" + query, "GET");
    const data = res.data || res;

    const posts = data.posts || data;
    if (!posts || posts.length === 0) {
      boardState.done = true;
      if (loadingEl) loadingEl.textContent = "게시글이 없습니다.";
      return;
    }

    boardState.posts = boardState.posts.concat(posts);

    if (data.has_next) {
      boardState.cursor = data.next_cursor;
    } else {
      boardState.done = true;
    }

    renderBoardList();
  } catch (e) {
    console.error("[loadPosts ERROR]", e);
    if (loadingEl) loadingEl.textContent = "게시글을 불러오지 못했습니다.";
  } finally {
    boardState.loading = false;
  }
}

function renderBoardList() {
  const listEl = document.getElementById("boardList");
  if (!listEl) return;

  listEl.innerHTML = boardState.posts
    .map((p) => {
      const authorName = p.user_nickname || `#${p.user_id}`;

      return `
        <article class="post-card" data-id="${p.post_id}">
          <h3 class="post-title">${escapeHtml(p.title)}</h3>
          <div class="post-meta">
            <span>${escapeHtml(authorName)}</span>
            <span>좋아요 ${p.like_count || 0}</span>
            <span>댓글 ${p.comments ? p.comments.length : 0}</span>
            <span>조회수 ${p.view_count || 0}</span>
          </div>
        </article>
      `;
    })
    .join("");

  // 카드 클릭 -> 상세로 이동
  listEl.querySelectorAll(".post-card").forEach((card) => {
    card.addEventListener("click", () => {
      const id = card.getAttribute("data-id");
      navigate(`#post?id=${id}`);
    });
  });
}

function renderBoard() {
  if (!requireLogin()) return;
  currentPostId = null; 
  // 상태 초기화
  boardState = {
    cursor: null,
    loading: false,
    done: false,
    posts: [],
  };

  app.innerHTML = `
    ${renderHeader()}
    <main class="page board-page">
      <section class="board-header">
        <h2>과즙상 모임 게시판</h2>
        <button class="primary-btn" id="btnGoWrite">게시글 작성</button>
      </section>
      <section id="boardList" class="board-list">
        <!-- 게시글 카드들 -->
      </section>
      <div id="boardLoading" class="board-loading">불러오는 중...</div>
    </main>
  `;

  bindHeaderEvents();

  document.getElementById("btnGoWrite").addEventListener("click", () => {
    navigate("#post-write");
  });

  // 스크롤 이벤트 (window 기준)
  window.onscroll = () => {
    if (boardState.loading || boardState.done) return;
    const scrollBottom =
      window.innerHeight + window.scrollY >= document.body.offsetHeight - 200;
    if (scrollBottom) {
      loadPosts();
    }
  };

  // 첫 로드
  loadPosts();
}



// =============================
// 게시글 상세 화면
// =============================
async function renderPostDetail() {
  if (!requireLogin()) return;
  const { id } = getQueryParams();
  if (!id) {
    alert("잘못된 접근입니다.");
    navigate("#board");
    return;
  }

  // ✅ 동일 게시글에 대한 중복 호출 막기
  if (currentPostId === id) {
    console.log("[renderPostDetail] same post, skip:", id);
    
  }
  currentPostId = id;

  console.log("[renderPostDetail] fetch /posts/" + id);

  app.innerHTML = `
    ${renderHeader()}
    <main class="page post-page">
      <section class="card" id="postDetailContainer">
        게시글을 불러오는 중입니다...
      </section>
    </main>
  `;

  bindHeaderEvents();

  try {
    const res = await apiRequest(`/posts/${id}`, "GET");
    const data = res.data || res;

    const user = getUser();
    const isWriter = user && user.user_id === data.user_id;
    const authorName = data.user_nickname || `#${data.user_id}`;
    const likeCount = data.like_count || 0;
    const commentsHtml = (data.comments || [])
      .map(
        (c) => `
        <div class="comment" data-cid="${c.comment_id}">
          <div class="comment-top">
            <span class="comment-author">#${c.user_id}</span>
            ${
              user && user.user_id === c.user_id
                ? `<button class="text-btn small edit-comment">수정</button>`
                : ""
            }
          </div>
          <div class="comment-content">${escapeHtml(c.content)}</div>
        </div>
      `
      )
      .join("");

    document.getElementById("postDetailContainer").innerHTML = `
    <div class="post-detail-header-row">
    <div>
      <button class="text-btn" id="btnBackToBoard">목록으로</button>
    </div>
    <button class="like-toggle-btn" id="btnToggleLike">
      <span class="like-icon">♡</span>
      <span class="like-count">${likeCount}</span>
    </button>
  </div>

  <h2 class="post-detail-title">${escapeHtml(data.title)}</h2>

  <div class="post-detail-meta">
    <span class="post-author">${escapeHtml(authorName)}</span>
    <span>조회수 ${data.view_count || 0}</span>
  </div>

  ${data.image
      ? `<img src="${escapeHtml(data.image)}" class="post-detail-image" />`
      : ""
  }

  <p class="post-detail-content">${escapeHtml(data.content)}</p>

  <div class="post-detail-actions">
    ${
      isWriter
        ? `<button class="secondary-btn" id="btnEditPost">수정</button>
           <button class="danger-btn" id="btnDeletePost">삭제</button>`
        : ""
    }
  </div>

  <hr />

  <section class="comment-section">
    <h3>댓글</h3>
    <div id="commentList">
      ${commentsHtml || "<p>아직 댓글이 없습니다.</p>"}
    </div>

    <div class="comment-form">
      <textarea id="commentInput" rows="3" placeholder="댓글을 남겨보세요."></textarea>
      <button class="primary-btn" id="btnAddComment">댓글 등록</button>
    </div>
  </section>
`;

    // 버튼 이벤트
    const btnBack = document.getElementById("btnBackToBoard");
    if (btnBack) {
      btnBack.addEventListener("click", () => navigate("#board"));
    }

    const btnEdit = document.getElementById("btnEditPost");
    if (btnEdit) {
      btnEdit.addEventListener("click", () => navigate(`#post-edit?id=${id}`));
    }

    const btnDelete = document.getElementById("btnDeletePost");
    if (btnDelete) {
      btnDelete.addEventListener("click", async () => {
        if (!confirm("게시글을 삭제하시겠습니까? 삭제 후에는 복구할 수 없습니다.")) {
          return;
        }
        try {
          await apiRequest(`/posts/${id}`, "DELETE");
          alert("삭제되었습니다.");
          navigate("#board");
        } catch (e) {}
      });
    }

    // 좋아요 토글
    const btnLike = document.getElementById("btnToggleLike");
    if (btnLike) {
      let liked = false;
      let count = likeCount;

      const iconEl = btnLike.querySelector(".like-icon");
      const countEl = btnLike.querySelector(".like-count");

      const applyState = () => {
        btnLike.classList.toggle("liked", liked);
        iconEl.textContent = liked ? "♥" : "♡";
        countEl.textContent = count;
      };
      applyState();

      btnLike.addEventListener("click", async (e) => {
        e.stopPropagation(); // 카드 클릭으로 상세 다시 열리는거 방지용

        liked = !liked;
        count += liked ? 1 : -1;
        if (count < 0) count = 0;
        applyState();

        try {
          // 백엔드 연동 (위에서 /posts/{id}/like 만든 경우)
          await apiRequest(`/posts/${id}/like`, "POST", { is_like: liked });
        } catch (err) {
          // 실패 시 롤백
          liked = !liked;
          count += liked ? 1 : -1;
          if (count < 0) count = 0;
          applyState();
          alert("좋아요 처리에 실패했어요.");
        }
      });
    }

    // 댓글 등록
    document.getElementById("btnAddComment").addEventListener("click", async () => {
      const content = document.getElementById("commentInput").value.trim();
      if (!content) {
        alert("댓글 내용을 입력해주세요.");
        return;
      }

      try {
        await apiRequest(`/posts/${id}/comments`, "POST", { content });
        alert("댓글이 등록되었습니다.");
        renderPostDetail(); // 새로고침
      } catch (e) {}
    });

    // 댓글 수정
    document.querySelectorAll(".edit-comment").forEach((btn) => {
      btn.addEventListener("click", async (e) => {
        const commentEl = e.target.closest(".comment");
        const cid = commentEl.getAttribute("data-cid");
        const oldContent = commentEl.querySelector(".comment-content").innerText;

        const newContent = prompt("댓글 수정", oldContent);
        if (!newContent || newContent.trim() === "") return;

        try {
          await apiRequest(
            `/posts/${id}/comments/${cid}`,
            "PATCH",
            { content: newContent.trim() }
          );
          alert("댓글이 수정되었습니다.");
          renderPostDetail();
        } catch (e) {}
      });
    });
  } catch (e) {
    console.error("[renderPostDetail] ERROR:", e);
    document.getElementById("postDetailContainer").innerHTML =
      "<p class='error-text'>게시글을 불러오지 못했습니다.</p>";
  }
}

// =============================
// 게시글 작성 화면
// =============================
function renderPostWrite() {
  if (!requireLogin()) return;

  app.innerHTML = `
    ${renderHeader()}
    <main class="page post-edit-page">
      <section class="card">
        <h2>게시글 작성</h2>
        <div class="form-group">
          <label>제목 *</label>
          <input type="text" id="writeTitle" placeholder="제목을 입력하세요." />
        </div>
        <div class="form-group">
          <label>내용 *</label>
          <textarea id="writeContent" rows="8" placeholder="내용을 입력하세요."></textarea>
        </div>
        <div class="form-group">
          <label>이미지 (URL)</label>
          <input type="text" id="writeImage" placeholder="이미지 URL (선택)" />
        </div>
        <button class="primary-btn full" id="btnSubmitPost">완료</button>
        <button class="text-btn" id="btnCancelWrite">취소</button>
      </section>
    </main>
  `;

  bindHeaderEvents();

  document.getElementById("btnCancelWrite").addEventListener("click", () => {
    navigate("#board");
  });

  document.getElementById("btnSubmitPost").addEventListener("click", async () => {
    const title = document.getElementById("writeTitle").value.trim();
    const content = document.getElementById("writeContent").value.trim();
    const image = document.getElementById("writeImage").value.trim();

    if (!title || !content) {
      alert("제목과 내용을 모두 입력해주세요.");
      return;
    }

    try {
      const body = { title, content, image: image || null };
      const res = await apiRequest("/posts", "POST", body);
      const postId = res.data?.post_id || res.post_id;
      alert("게시글이 등록되었습니다.");
      if (postId) navigate(`#post?id=${postId}`);
      else navigate("#board");
    } catch (e) {}
  });
}

// =============================
// 게시글 수정 화면
// =============================
async function renderPostEdit() {
  if (!requireLogin()) return;
  const { id } = getQueryParams();
  if (!id) {
    alert("잘못된 접근입니다.");
    navigate("#board");
    return;
  }

  app.innerHTML = `
    ${renderHeader()}
    <main class="page post-edit-page">
      <section class="card" id="postEditContainer">
        게시글 정보를 불러오는 중입니다...
      </section>
    </main>
  `;

  bindHeaderEvents();

  try {
    const res = await apiRequest(`/posts/${id}`, "GET");
    const data = res.data || res;

    document.getElementById("postEditContainer").innerHTML = `
      <h2>게시글 수정</h2>
      <div class="form-group">
        <label>제목 *</label>
        <input type="text" id="editTitle" value="${escapeHtml(
          data.title
        )}" />
      </div>
      <div class="form-group">
        <label>내용 *</label>
        <textarea id="editContent" rows="8">${escapeHtml(
          data.content
        )}</textarea>
      </div>
      <div class="form-group">
        <label>이미지 (URL)</label>
        <input type="text" id="editImage" value="${escapeHtml(
          data.image || ""
        )}" />
      </div>
      <button class="primary-btn full" id="btnUpdatePost">수정하기</button>
      <button class="text-btn" id="btnCancelEdit">취소</button>
    `;

    document.getElementById("btnCancelEdit").addEventListener("click", () => {
      navigate(`#post?id=${id}`);
    });

    document.getElementById("btnUpdatePost").addEventListener("click", async () => {
      const title = document.getElementById("editTitle").value.trim();
      const content = document.getElementById("editContent").value.trim();
      const image = document.getElementById("editImage").value.trim();

      if (!title || !content) {
        alert("제목과 내용을 모두 입력해주세요.");
        return;
      }

      try {
        await apiRequest(`/posts/${id}`, "PATCH", {
          title,
          content,
          image: image || null,
        });
        alert("수정되었습니다.");
        navigate(`#post?id=${id}`);
      } catch (e) {}
    });
  } catch (e) {
    document.getElementById("postEditContainer").innerHTML =
      "<p class='error-text'>게시글 정보를 불러오지 못했습니다.</p>";
  }
}