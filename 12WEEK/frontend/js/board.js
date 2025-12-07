

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
      const authorName = p.user_nickname || `${p.user_id}`;

      return `
        <article class="post-card" data-id="${p.post_id}">
          <h3 class="post-title">${escapeHtml(p.title)}</h3>
          <div class="post-meta">
            <span>${escapeHtml(authorName)}</span>
            <span>-</span>
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
            <span class="comment-author">${c.user_nickname}</span>
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
     ? `<img src="${API_BASE}${escapeHtml(data.image)}" class="post-detail-image" />`
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
      <textarea
        id="commentInput"
        class="textarea"
        rows="3"
        placeholder="댓글을 남겨보세요."></textarea>
      <div class="comment-form-actions">
        <button class="primary-btn" id="btnAddComment">댓글 등록</button>
      </div>
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
// 게시글 작성 화면 (수정 완료)
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
          <label>이미지</label>
          <input type="file" id="writeImage" accept="image/*" />
          <div class="image-preview-wrapper" style="margin-top:8px;">
            <img id="writeImagePreview" class="image-preview" style="display:none; max-width:100%; border-radius:8px;" />
          </div>
        </div>
        <button type="button" class="primary-btn full" id="btnSubmitPost">완료</button>
        <button type="button" class="text-btn" id="btnCancelWrite">취소</button>
      </section>
    </main>
  `;

  bindHeaderEvents();

  // --- 변수 설정 ---
  let uploadedImageUrl = null; // ★ 서버에서 받은 진짜 이미지 주소를 저장할 변수
  const fileInput = document.getElementById("writeImage");
  const previewEl = document.getElementById("writeImagePreview");

  // --- 취소 버튼 ---
  document.getElementById("btnCancelWrite").addEventListener("click", () => {
    navigate("#board");
  });

  // --- [1단계] 파일 선택 시: 미리보기 + 서버 업로드 ---
  fileInput.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    
    if (file) {
      // 1-1. 화면에 미리보기 (FileReader 사용)
      const reader = new FileReader();
      reader.onload = (event) => {
        previewEl.src = event.target.result;
        previewEl.style.display = "block";
      };
      reader.readAsDataURL(file);

      // 1-2. ★ 서버로 실제 파일 전송 (/upload/image)
      try {
        const formData = new FormData();
        formData.append("file", file);

        // 이미지 업로드는 isFile=true로 보냄
        const res = await apiRequest("/upload/image", "POST", formData, true);
        
        // 서버가 돌려준 진짜 URL 저장 (예: /media/post_images/uuid.jpg)
        uploadedImageUrl = res.url || (res.data && res.data.url);
        console.log("이미지 업로드 성공, URL:", uploadedImageUrl);

      } catch (err) { // 변수명 err로 통일
        console.error("업로드 실패:", err);
        alert("이미지 업로드에 실패했습니다.");
        // 실패 시 미리보기 감추기
        previewEl.style.display = "none";
        fileInput.value = "";
      }
    } else {
        // 파일 선택 취소 시 초기화
        previewEl.src = "";
        previewEl.style.display = "none";
        uploadedImageUrl = null;
    }
  });
  
  // --- [2단계] 완료 버튼: 게시글 정보 전송 (/posts) ---
  document.getElementById("btnSubmitPost").addEventListener("click", async () => {
    const title = document.getElementById("writeTitle").value.trim();
    const content = document.getElementById("writeContent").value.trim();
    
    // ★ 여기서 .value가 아니라 아까 저장해둔 URL 변수(uploadedImageUrl)를 사용해야 합니다!
    const image = uploadedImageUrl; 

    if (!title || !content) {
      alert("제목과 내용을 모두 입력해주세요.");
      return;
    }

    try {
      const body = { title, content, image: image || null };
      
      // ★ 게시글 작성은 JSON이므로 isFile=false(기본값)로 보내야 합니다. (4번째 인자 생략)
      const res = await apiRequest("/posts", "POST", body); 
      
      const postId = res.data?.post_id || res.post_id;
      
      alert("게시글이 등록되었습니다.");
      if (postId) navigate(`#post?id=${postId}`);
      else navigate("#board");

    } catch (e) { // 여기서는 e를 사용
      console.error("게시글 등록 실패:", e);
      // alert는 apiRequest에서 띄우므로 생략 가능하지만 필요시 추가
    }
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

    // 여기서 수정 폼 표시
    document.getElementById("postEditContainer").innerHTML = `
      <h2>게시글 수정</h2>
      <div class="form-group">
        <label>제목 *</label>
        <input type="text" id="editTitle" value="${escapeHtml(data.title)}" />
      </div>
      <div class="form-group">
        <label>내용 *</label>
        <textarea id="editContent" rows="8">${escapeHtml(
          data.content
        )}</textarea>
      </div>
      <div class="form-group">
        <label>이미지</label>
        <input type="file" id="editImageFile" accept="image/*" />
        <div class="image-preview-wrapper" style="margin-top:8px;">
          ${
            data.image
              ? `<img src="${API_BASE}${escapeHtml(
                  data.image
                )}" id="editImagePreview" class="image-preview" />`
              : `<img id="editImagePreview" class="image-preview" style="display:none;" />`
          }
        </div>
      </div>
      <button class="primary-btn full" id="btnUpdatePost">수정하기</button>
      <button class="text-btn" id="btnCancelEdit">취소</button>
    `;

    // 업로드된 이미지 URL을 저장할 변수 (초기값: 기존 이미지)
    let uploadedImageUrl = data.image || null;

    const fileInput = document.getElementById("editImageFile");
    const previewEl = document.getElementById("editImagePreview");

    // 파일 선택 시 업로드 + 미리보기
    if (fileInput) {
      fileInput.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("file", file);

        try {
          // 업로드 API는 실제 엔드포인트에 맞게 수정
          const res = await apiRequest("/upload/image", "POST", formData, true);
          const url = res.data?.url || res.url;

          uploadedImageUrl = url;
          previewEl.src = url;
          previewEl.style.display = "block";
        } catch (err) {
          console.error(err);
          alert("이미지 업로드에 실패했습니다.");
        }
      });
    }

    // 취소 버튼
    document.getElementById("btnCancelEdit").addEventListener("click", () => {
      navigate(`#post?id=${id}`);
    });

    // 수정하기 버튼
    document.getElementById("btnUpdatePost").addEventListener("click", async () => {
      const title = document.getElementById("editTitle").value.trim();
      const content = document.getElementById("editContent").value.trim();

      if (!title || !content) {
        alert("제목과 내용을 모두 입력해주세요.");
        return;
      }

      try {
        await apiRequest(`/posts/${id}`, "PATCH", {
          title,
          content,
          image: uploadedImageUrl || null,   // 여기서 URL 사용
        });
        alert("수정되었습니다.");
        navigate(`#post?id=${id}`);
      } catch (e) {
        console.error(e);
        alert("수정에 실패했습니다.");
      }
    });
  } catch (e) {
    console.error(e);
    document.getElementById("postEditContainer").innerHTML =
      "<p class='error-text'>게시글 정보를 불러오지 못했습니다.</p>";
  }
}