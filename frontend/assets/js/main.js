// DOM Elements
const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const chatForm = document.getElementById("chat-form");
const uploadBtn = document.getElementById("upload-btn");
const quickActions = document.getElementById("quick-actions");
const typingIndicator = document.getElementById("typing-indicator");

// Modal elements
const uploadModal = document.getElementById("uploadModal");
const closeModal = document.getElementById("closeModal");
const modalMessage = document.getElementById("modalMessage");
const modalUploadArea = document.getElementById("modalUploadArea");
const modalUploadBtn = document.getElementById("modalUploadBtn");
const modalFileInput = document.getElementById("modalFileInput");
const modalPreview = document.getElementById("modalPreview");
const modalPreviewImage = document.getElementById("modalPreviewImage");
const modalFileName = document.getElementById("modalFileName");
const modalFileSize = document.getElementById("modalFileSize");
const modalProcessBtn = document.getElementById("modalProcessBtn");
const modalCancelBtn = document.getElementById("modalCancelBtn");
const modalLoading = document.getElementById("modalLoading");

// Camera elements
const cameraModal = document.getElementById("cameraModal");
const closeCamera = document.getElementById("closeCamera");
const cameraVideo = document.getElementById("cameraVideo");
const cameraCanvas = document.getElementById("cameraCanvas");
const startVerifyBtn = document.getElementById("startVerifyBtn");
const stopVerifyBtn = document.getElementById("stopVerifyBtn");
const realtimeResult = document.getElementById("realtimeResult");
const verificationStatus = document.getElementById("verificationStatus");
const similarityBar = document.getElementById("similarityBar");
const similarityFill = document.getElementById("similarityFill");
const similarityText = document.getElementById("similarityText");
const verificationMessage = document.getElementById("verificationMessage");
const cameraLoading = document.getElementById("cameraLoading");
const cameraMessage = document.getElementById("cameraMessage");

// Debug: Kiểm tra xem các elements có được tìm thấy không
console.log("Camera elements check:");
console.log("cameraModal:", cameraModal);
console.log("cameraVideo:", cameraVideo);
console.log("cameraMessage:", cameraMessage);
console.log("startVerifyBtn:", startVerifyBtn);
console.log("realtimeResult:", realtimeResult);

let modalSelectedFile = null;
let idCardUrl = null; // Lưu URL của ảnh căn cước để xác thực
let cameraStream = null; // Lưu camera stream
let capturedImageData = null; // Lưu dữ liệu ảnh đã chụp
let isRealtimeVerifying = false; // Trạng thái xác thực realtime
let verificationInterval = null; // Interval cho xác thực realtime
let websocket = null; // WebSocket connection
let frameCount = 0; // Đếm frame để gửi
const SEND_INTERVAL = 30; // Gửi mỗi 30 frame

// Global variables for streaming
let currentThinkingElement = null;
let currentMessageElement = null;
let isStreaming = false;
let useStreamingMode = true; // Set to true to enable streaming mode

// Chat Form Events
chatForm.addEventListener("submit", handleSubmit);
uploadBtn.addEventListener("click", () =>
  openUploadModal("ກະລຸນາອັບໂຫຼດຮູບບັດປະຈໍາຕົວຂອງທ່ານ")
);

// Quick Actions Events
quickActions.addEventListener("click", (e) => {
  const quickAction = e.target.closest(".quick-action-item");
  if (quickAction) {
    const message = quickAction.getAttribute("data-message");
    const action = quickAction.getAttribute("data-action");

    if (action === "camera-test") {
      // Test camera modal
      openCameraRealtimeModal(
        "ນີ້ແມ່ນການທົດສອບກ້ອງຖ່າຍຮູບ. ກະລຸນາຖ່າຍຮູບເພື່ອທົດສອບຄຸນສົມບັດກ້ອງ.",
        null // Không có id_card_url cho test
      );
    } else if (message) {
      userInput.value = message;
      handleSubmit(e);
    }
  }
});

// Chat Functions
function handleSubmit(e) {
  e.preventDefault();
  const message = userInput.value.trim();
  if (!message) return;

  // Add user message to chat
  addMessage(message, "user");
  userInput.value = "";

  // Show typing indicator
  showTypingIndicator();

  // Choose between streaming or regular mode
  if (useStreamingMode) {
    handleStreamingChat(message);
  } else {
    handleRegularChat(message);
  }
}

function handleRegularChat(message) {
  // Send to server (old method)
  fetch("/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: message }),
  })
    .then((response) => response.json())
    .then((data) => {
      hideTypingIndicator();

      if (data.success) {
        // Check if response contains tool calls
        if (data.tool_calls) {
          handleToolCalls(data.tool_calls);
        } else {
          addMessage(formatChatbotResponse(data.response), "bot");
        }
      } else {
        addMessage(
          "ຂໍ້ຜິດພາດ: " + (data.error || "ມີຂໍ້ຜິດພາດເກີດຂຶ້ນ"),
          "bot"
        );
      }
    })
    .catch((error) => {
      hideTypingIndicator();
      addMessage("ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່: " + error.message, "bot");
    });
}

function handleStreamingChat(message) {
  // Reset streaming state
  currentThinkingElement = null;
  currentMessageElement = null;
  isStreaming = true;

  let fullContent = "";
  let fullThinking = "";
  let hasToolCalls = false;
  let toolCalls = null;

  // Create EventSource for Server-Sent Events
  fetch("/chat-stream", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message: message }),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      function processStream() {
        return reader.read().then(({ done, value }) => {
          if (done) {
            // Stream finished
            hideTypingIndicator();
            isStreaming = false;

            // Remove streaming cursor if exists
            if (currentMessageElement) {
              const cursor =
                currentMessageElement.querySelector(".streaming-cursor");
              if (cursor) cursor.remove();
            }

            // Handle tool calls if any
            if (hasToolCalls && toolCalls) {
              handleToolCalls(toolCalls);
            }

            return;
          }

          // Process the chunk
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          lines.forEach((line) => {
            if (line.startsWith("data: ")) {
              const dataStr = line.substring(6).trim();

              if (dataStr === "[DONE]") {
                return;
              }

              try {
                const data = JSON.parse(dataStr);
                handleStreamChunk(data);

                // Save data for later use
                if (data.type === "thinking") {
                  fullThinking = data.full_thinking || fullThinking;
                }
                if (data.type === "content") {
                  fullContent = data.full_content || fullContent;
                }
                if (data.type === "tool_calls") {
                  hasToolCalls = true;
                  toolCalls = data.tool_calls;
                }
                if (data.type === "done") {
                  if (data.tool_calls) {
                    hasToolCalls = true;
                    toolCalls = data.tool_calls;
                  }
                }
              } catch (e) {
                console.error("Error parsing stream data:", e, dataStr);
              }
            }
          });

          // Continue reading
          return processStream();
        });
      }

      return processStream();
    })
    .catch((error) => {
      hideTypingIndicator();
      isStreaming = false;
      console.error("Streaming error:", error);
      addMessage("ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່: " + error.message, "bot");
    });
}

function handleStreamChunk(data) {
  switch (data.type) {
    case "thinking":
      handleThinkingChunk(data);
      break;
    case "thinking_done":
      markThinkingDone(data);
      break;
    case "content":
      handleContentChunk(data);
      break;
    case "tool_calls":
      // Tool calls will be handled after stream is done
      break;
    case "done":
      // Stream done
      hideTypingIndicator();
      break;
    case "error":
      hideTypingIndicator();
      addMessage("ຂໍ້ຜິດພາດ: " + data.error, "bot");
      break;
  }
}

function handleThinkingChunk(data) {
  if (!currentThinkingElement) {
    // Create thinking container
    hideTypingIndicator();
    currentThinkingElement = createThinkingElement();
    chatBox.appendChild(currentThinkingElement);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Update thinking text
  const thinkingText = currentThinkingElement.querySelector(".thinking-text");
  if (thinkingText) {
    thinkingText.textContent = data.full_thinking || data.content;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

function markThinkingDone(data) {
  if (currentThinkingElement) {
    currentThinkingElement.classList.add("done");
    const icon = currentThinkingElement.querySelector(".thinking-icon");
    if (icon) {
      icon.innerHTML = '<i class="fas fa-check-circle"></i>';
    }
    const label = currentThinkingElement.querySelector(".thinking-label");
    if (label) {
      const dotsContainer = label.querySelector(".thinking-dots");
      if (dotsContainer) {
        dotsContainer.remove();
      }
      label.innerHTML = "ສຳເລັດການວິເຄາະ";
    }
  }
}

function handleContentChunk(data) {
  if (!currentMessageElement) {
    // Create message element
    const messageDiv = document.createElement("div");
    messageDiv.className = "bot-message";

    const messageContent = document.createElement("div");
    messageContent.className = "message-content";

    const messageAvatar = document.createElement("div");
    messageAvatar.className = "message-avatar";
    messageAvatar.innerHTML = '<i class="fas fa-robot"></i>';

    const messageBubble = document.createElement("div");
    messageBubble.className = "message-bubble bot-bubble";
    messageBubble.innerHTML = '<span class="streaming-cursor"></span>';

    const messageTime = document.createElement("div");
    messageTime.className = "message-time";
    messageTime.textContent = new Date().toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });

    messageContent.appendChild(messageAvatar);
    messageContent.appendChild(messageBubble);
    messageContent.appendChild(messageTime);
    messageDiv.appendChild(messageContent);

    chatBox.appendChild(messageDiv);
    currentMessageElement = messageBubble;
  }

  // Update content
  const cursor = currentMessageElement.querySelector(".streaming-cursor");
  const formattedContent = formatChatbotResponse(
    data.full_content || data.content
  );

  if (cursor) {
    currentMessageElement.innerHTML =
      formattedContent + '<span class="streaming-cursor"></span>';
  } else {
    currentMessageElement.innerHTML = formattedContent;
  }

  chatBox.scrollTop = chatBox.scrollHeight;
}

function createThinkingElement() {
  const thinkingDiv = document.createElement("div");
  thinkingDiv.className = "thinking-container";
  thinkingDiv.innerHTML = `
        <div class="thinking-icon">
            <i class="fas fa-brain"></i>
        </div>
        <div class="thinking-content">
            <div class="thinking-label">
                ກຳລັງວິເຄາະ
                <span class="thinking-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </span>
            </div>
            <div class="thinking-text"></div>
        </div>
    `;
  return thinkingDiv;
}

function addRetryVerificationButton() {
  const retryButton = document.createElement("div");
  retryButton.className = "retry-verification-btn";
  retryButton.innerHTML = `
    <button class="btn btn-warning" onclick="retryVerification()">
      <i class="fas fa-redo"></i> ຢັ້ງຢືນອີກຄັ້ງ
    </button>
  `;

  // Thêm vào chat box
  chatBox.appendChild(retryButton);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function retryVerification() {
  // Xóa nút retry
  const retryBtn = document.querySelector(".retry-verification-btn");
  if (retryBtn) {
    retryBtn.remove();
  }

  // Mở camera lại để xác thực
  addMessage("ກະລຸນາຢັ້ງຢືນໃບໜ້າອີກຄັ້ງດ້ວຍກ້ອງຖ່າຍຮູບ", "bot");

  // Tìm lại id_card_url từ conversation history
  // Tạm thời sử dụng một URL test - trong thực tế sẽ lấy từ conversation
  const testIdCardUrl = "https://example.com/test-id-card.jpg";

  setTimeout(() => {
    openCameraRealtimeModal(
      "ກະລຸນາຖ່າຍຮູບ selfie ເພື່ອຢັ້ງຢືນໃບໜ້າອີກຄັ້ງ",
      testIdCardUrl
    );
  }, 1000);
}

function addMessage(content, sender) {
  const messageDiv = document.createElement("div");
  messageDiv.className = `${sender}-message`;

  const messageContent = document.createElement("div");
  messageContent.className = "message-content";

  const messageBubble = document.createElement("div");
  messageBubble.className = `message-bubble ${sender}-bubble`;
  messageBubble.innerHTML = content;

  const messageTime = document.createElement("div");
  messageTime.className = "message-time";
  messageTime.textContent = new Date().toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (sender === "bot") {
    const messageAvatar = document.createElement("div");
    messageAvatar.className = "message-avatar";
    messageAvatar.innerHTML = '<i class="fas fa-robot"></i>';
    messageContent.appendChild(messageAvatar);
  }

  messageContent.appendChild(messageBubble);
  messageContent.appendChild(messageTime);
  messageDiv.appendChild(messageContent);

  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
  typingIndicator.style.display = "flex";
  chatBox.scrollTop = chatBox.scrollHeight;
}

function hideTypingIndicator() {
  typingIndicator.style.display = "none";
}

function formatFileSize(bytes) {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

function formatScanResult(scanResult) {
  if (!scanResult) return "<p>ບໍ່ມີຂໍ້ມູນ</p>";

  let html = '<div class="scan-result">';

  if (scanResult.text) {
    html += `<h4><i class="fas fa-text-width"></i> ຂໍ້ຄວາມທີ່ສະກັດໄດ້:</h4>`;
    html += `<p class="extracted-text">${scanResult.text}</p>`;
  }

  if (scanResult.document_type) {
    html += `<h4><i class="fas fa-id-card"></i> ປະເພດເອກະສານ:</h4>`;
    html += `<p class="document-type">${scanResult.document_type}</p>`;
  }

  if (scanResult.display_name) {
    html += `<h4><i class="fas fa-user"></i> ຊື່ສະແດງ:</h4>`;
    html += `<p class="display-name">${scanResult.display_name}</p>`;
  }

  // Add other fields if they exist
  Object.keys(scanResult).forEach((key) => {
    if (
      !["text", "document_type", "display_name", "img_base64"].includes(key)
    ) {
      html += `<h4><i class="fas fa-info-circle"></i> ${key}:</h4>`;
      html += `<p>${scanResult[key]}</p>`;
    }
  });

  html += "</div>";
  return html;
}

function formatMarkdownToHtml(markdownText) {
  if (!markdownText) return "<p>ບໍ່ມີເນື້ອຫາ</p>";

  let html = '<div class="chatbot-response">';

  // Split into lines for processing
  const lines = markdownText.split("\n");
  let inList = false;
  let inCodeBlock = false;

  for (let line of lines) {
    line = line.trim();

    // Skip empty lines
    if (!line) {
      if (inList) {
        html += "</ul>";
        inList = false;
      }
      html += "<br>";
      continue;
    }

    // Code blocks
    if (line.startsWith("```")) {
      if (!inCodeBlock) {
        html += '<div class="code-block"><pre><code>';
        inCodeBlock = true;
      } else {
        html += "</code></pre></div>";
        inCodeBlock = false;
      }
      continue;
    }

    if (inCodeBlock) {
      html += `${line}\n`;
      continue;
    }

    // Headers
    if (line.startsWith("#")) {
      const level = line.length - line.replace(/^#+/, "").length;
      const headerText = line.replace(/^#+\s*/, "").trim();
      html += `<h${Math.min(
        level,
        6
      )} class="response-header">${headerText}</h${Math.min(level, 6)}>`;
      continue;
    }

    // Lists
    if (line.startsWith("- ") || line.startsWith("* ")) {
      if (!inList) {
        html += '<ul class="response-list">';
        inList = true;
      }
      const itemText = line.substring(2).trim();
      const processedText = processInlineFormatting(itemText);
      html += `<li class="response-list-item">${processedText}</li>`;
      continue;
    }

    // Numbered lists
    if (/^\d+\.\s/.test(line)) {
      if (!inList) {
        html += '<ol class="response-list">';
        inList = true;
      }
      const itemText = line.replace(/^\d+\.\s/, "").trim();
      const processedText = processInlineFormatting(itemText);
      html += `<li class="response-list-item">${processedText}</li>`;
      continue;
    }

    // End list if we hit a non-list item
    if (inList) {
      html += "</ul>";
      inList = false;
    }

    // Regular paragraphs
    if (line) {
      const processedLine = processInlineFormatting(line);
      html += `<p class="response-paragraph">${processedLine}</p>`;
    }
  }

  // Close any open list
  if (inList) {
    html += "</ul>";
  }

  html += "</div>";
  return html;
}

function processInlineFormatting(text) {
  // Bold text **text** or __text__
  text = text.replace(
    /\*\*(.*?)\*\*/g,
    '<strong class="response-bold">$1</strong>'
  );
  text = text.replace(
    /__(.*?)__/g,
    '<strong class="response-bold">$1</strong>'
  );

  // Italic text *text* or _text_
  text = text.replace(/\*(.*?)\*/g, '<em class="response-italic">$1</em>');
  text = text.replace(/_(.*?)_/g, '<em class="response-italic">$1</em>');

  // Inline code `code`
  text = text.replace(/`(.*?)`/g, '<code class="response-code">$1</code>');

  // Links [text](url)
  text = text.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" class="response-link" target="_blank">$1</a>'
  );

  return text;
}

function formatChatbotResponse(responseText) {
  if (!responseText) return "<p>ບໍ່ມີການຕອບກັບ</p>";

  // Check if it's already HTML
  if (responseText.trim().startsWith("<")) {
    return responseText;
  }

  // Convert Markdown to HTML
  return formatMarkdownToHtml(responseText);
}

function formatVerifyResult(verifyResult) {
  if (!verifyResult) return "<p>ບໍ່ມີຂໍ້ມູນການຢັ້ງຢືນ</p>";

  let html = '<div class="verify-result">';

  // Xử lý format mới từ WebSocket API
  if (verifyResult.status === "success") {
    html += `<h4><i class="fas fa-check-circle"></i> ສະຖານະ:</h4>`;
    html += `<p class="match-success">ຢັ້ງຢືນສຳເລັດ</p>`;

    if (verifyResult.same_person !== undefined) {
      const matchStatus = verifyResult.same_person
        ? "ເປັນຄົນດຽວກັນ"
        : "ບໍ່ແມ່ນຄົນດຽວກັນ";
      const matchClass = verifyResult.same_person
        ? "match-success"
        : "match-fail";
      html += `<h4><i class="fas fa-user-check"></i> ຜົນການຢັ້ງຢືນ:</h4>`;
      html += `<p class="${matchClass}">${matchStatus}</p>`;
    }

    if (verifyResult.similarity !== undefined) {
      html += `<h4><i class="fas fa-percentage"></i> ຄວາມຄ້າຍຄືກັນ:</h4>`;
      html += `<p class="match-score">${(verifyResult.similarity * 100).toFixed(
        2
      )}%</p>`;
    }
  } else {
    html += `<h4><i class="fas fa-times-circle"></i> ສະຖານະ:</h4>`;
    html += `<p class="match-fail">ຢັ້ງຢືນບໍ່ສຳເລັດ</p>`;

    // Hiển thị error message nếu có và không phải success
    if (verifyResult.error) {
      html += `<h4><i class="fas fa-exclamation-triangle"></i> ຂໍ້ຜິດພາດ:</h4>`;
      html += `<p>${verifyResult.error}</p>`;
    }
  }

  // Xử lý format cũ (backward compatibility)
  if (verifyResult.match_score !== undefined) {
    html += `<h4><i class="fas fa-percentage"></i> ຄະແນນການຈັບຄູ່:</h4>`;
    html += `<p class="match-score">${(verifyResult.match_score * 100).toFixed(
      2
    )}%</p>`;
  }

  if (verifyResult.is_match !== undefined) {
    const matchStatus = verifyResult.is_match ? "ຕົງກັນ" : "ບໍ່ຕົງກັນ";
    const matchClass = verifyResult.is_match ? "match-success" : "match-fail";
    html += `<h4><i class="fas fa-check-circle"></i> ຜົນການຢັ້ງຢືນ:</h4>`;
    html += `<p class="${matchClass}">${matchStatus}</p>`;
  }

  if (verifyResult.confidence !== undefined) {
    html += `<h4><i class="fas fa-chart-line"></i> ຄວາມໝັ້ນໃຈ:</h4>`;
    html += `<p class="confidence">${(verifyResult.confidence * 100).toFixed(
      2
    )}%</p>`;
  }

  // Add other fields if they exist (except bbox)
  Object.keys(verifyResult).forEach((key) => {
    if (
      ![
        "status",
        "same_person",
        "similarity",
        "msg",
        "match_score",
        "is_match",
        "confidence",
        "bbox",
      ].includes(key)
    ) {
      html += `<h4><i class="fas fa-info-circle"></i> ${key}:</h4>`;
      html += `<p>${verifyResult[key]}</p>`;
    }
  });

  html += "</div>";
  return html;
}

// Modal Events
closeModal.addEventListener("click", closeUploadModal);
modalUploadArea.addEventListener("click", () => modalFileInput.click());
modalUploadBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  modalFileInput.click();
});
modalFileInput.addEventListener("change", handleModalFileSelect);
modalProcessBtn.addEventListener("click", processModalImage);
modalCancelBtn.addEventListener("click", cancelModalUpload);

// Modal Drag and Drop Events
modalUploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  modalUploadArea.classList.add("dragover");
});

modalUploadArea.addEventListener("dragleave", () => {
  modalUploadArea.classList.remove("dragover");
});

modalUploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  modalUploadArea.classList.remove("dragover");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleModalFile(files[0]);
  }
});

// Close modal when clicking outside
uploadModal.addEventListener("click", (e) => {
  if (e.target === uploadModal) {
    closeUploadModal();
  }
});

// Camera Events
closeCamera.addEventListener("click", closeCameraModal);
startVerifyBtn.addEventListener("click", startRealtimeVerification);
stopVerifyBtn.addEventListener("click", stopRealtimeVerification);

// Close camera modal when clicking outside
cameraModal.addEventListener("click", (e) => {
  if (e.target === cameraModal) {
    closeCameraModal();
  }
});

// Handle tool calls from agent
function handleToolCalls(toolCalls) {
  toolCalls.forEach((toolCall) => {
    if (toolCall.function.name === "open_image_upload") {
      const args = JSON.parse(toolCall.function.arguments);
      openUploadModal(args.message);
    } else if (toolCall.function.name === "open_selfie_upload") {
      const args = JSON.parse(toolCall.function.arguments);
      openSelfieUploadModal(args.message, args.id_card_url);
    } else if (toolCall.function.name === "open_camera_realtime") {
      const args = JSON.parse(toolCall.function.arguments);
      openCameraRealtimeModal(args.message, args.id_card_url);
    }
  });
}

// Modal Functions
function openUploadModal(message) {
  modalMessage.textContent = message;
  modalSelectedFile = null;
  modalUploadArea.style.display = "block";
  modalPreview.style.display = "none";
  modalLoading.style.display = "none";
  uploadModal.style.display = "flex";
}

function openSelfieUploadModal(message, idCardUrlParam) {
  idCardUrl = idCardUrlParam; // Lưu URL căn cước
  modalMessage.textContent = message;
  modalSelectedFile = null;
  modalUploadArea.style.display = "block";
  modalPreview.style.display = "none";
  modalLoading.style.display = "none";
  uploadModal.style.display = "flex";
}

function closeUploadModal() {
  uploadModal.style.display = "none";
  modalSelectedFile = null;
  modalFileInput.value = "";
}

// Camera Functions
function openCameraRealtimeModal(message, idCardUrlParam) {
  console.log("Opening camera modal...", message, idCardUrlParam);
  idCardUrl = idCardUrlParam; // Lưu URL căn cước vào biến global
  cameraMessage.textContent = message;

  console.log("Camera modal element:", cameraModal);
  console.log("Camera modal display before:", cameraModal.style.display);

  cameraModal.style.display = "flex";
  realtimeResult.style.display = "none";
  cameraLoading.style.display = "none";
  capturedImageData = null;
  isRealtimeVerifying = false;

  console.log("Camera modal display after:", cameraModal.style.display);

  startCamera();
}

function startCamera() {
  console.log("Starting camera...");
  navigator.mediaDevices
    .getUserMedia({
      video: {
        width: { ideal: 640 },
        height: { ideal: 480 },
        facingMode: "user",
      },
    })
    .then((stream) => {
      console.log("Camera stream obtained:", stream);
      cameraStream = stream;
      cameraVideo.srcObject = stream;
      cameraVideo.play();
      startVerifyBtn.style.display = "inline-block";
      stopVerifyBtn.style.display = "none";
      console.log("Camera started successfully");
    })
    .catch((error) => {
      console.error("Error accessing camera:", error);
      addMessage(
        "ບໍ່ສາມາດເຂົ້າເຖິງກ້ອງຖ່າຍຮູບໄດ້. ກະລຸນາກວດສອບສິດໃນການເຂົ້າເຖິງກ້ອງຖ່າຍຮູບ.",
        "bot"
      );
      closeCameraModal();
    });
}

function startRealtimeVerification() {
  console.log("Starting realtime verification, idCardUrl:", idCardUrl); // Debug log

  if (!idCardUrl) {
    addMessage("ບໍ່ມີ URL ຮູບບັດປະຈໍາຕົວເພື່ອຢັ້ງຢືນ", "bot");
    return;
  }

  console.log("Starting realtime verification...");
  isRealtimeVerifying = true;

  // Hiển thị UI realtime
  startVerifyBtn.style.display = "none";
  stopVerifyBtn.style.display = "inline-block";
  realtimeResult.style.display = "block";

  // Reset UI
  updateVerificationStatus("ກຳລັງເຊື່ອມຕໍ່...", "verifying", 0);
  verificationMessage.textContent = "ກຳລັງເຊື່ອມຕໍ່ຫາ server ຢັ້ງຢືນ";

  // Kết nối WebSocket
  connectWebSocket();
}

function connectWebSocket() {
  // Kết nối đến Flask server để thiết lập WebSocket
  fetch("/start-websocket-verification", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      id_card_image_url: idCardUrl,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        updateVerificationStatus("ກຳລັງຢັ້ງຢືນ...", "verifying", 0);
        verificationMessage.textContent = "ກະລຸນາເບິ່ງກ້ອງໂດຍກົງ";

        // Bắt đầu gửi frame
        startFrameCapture();
      } else {
        updateVerificationStatus("ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່", "failed", 0);
        verificationMessage.textContent =
          "ບໍ່ສາມາດເຊື່ອມຕໍ່ຫາ server: " + data.error;
      }
    })
    .catch((error) => {
      console.error("WebSocket connection error:", error);
      updateVerificationStatus("ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່", "failed", 0);
      verificationMessage.textContent = "ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່ຫາ server";
    });
}

function startFrameCapture() {
  // Bắt đầu capture frame từ video
  verificationInterval = setInterval(() => {
    captureAndSendFrame();
  }, 100); // Capture mỗi 100ms
}

function captureAndSendFrame() {
  if (!isRealtimeVerifying || !cameraVideo.videoWidth) {
    return;
  }

  frameCount++;

  // Chỉ gửi mỗi SEND_INTERVAL frame
  if (frameCount % SEND_INTERVAL === 0) {
    // Chụp frame từ video
    const context = cameraCanvas.getContext("2d");
    cameraCanvas.width = cameraVideo.videoWidth;
    cameraCanvas.height = cameraVideo.videoHeight;
    context.drawImage(cameraVideo, 0, 0);

    // Chuyển đổi thành base64 (loại bỏ data URL prefix)
    const frameBase64 = cameraCanvas.toDataURL("image/jpeg", 0.8).split(",")[1];

    // Gửi frame qua WebSocket
    sendFrameToWebSocket(frameBase64);
  }
}

function sendFrameToWebSocket(frameBase64) {
  fetch("/send-frame", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      frame_base64: frameBase64,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success && data.result) {
        const result = data.result;
        const similarity = result.similarity || 0;
        const isMatch = result.same_person === true;

        // Cập nhật UI
        if (isMatch && similarity > 0.8) {
          updateVerificationStatus("ຢັ້ງຢືນສຳເລັດ!", "success", similarity);
          verificationMessage.textContent = "ໃບໜ້າຖືກຢັ້ງຢືນສຳເລັດແລ້ວ!";

          // Tự động dừng sau 3 giây
          setTimeout(() => {
            stopRealtimeVerification();
            closeCameraModal();
            addMessage("ຢັ້ງຢືນໃບໜ້າສຳເລັດ!", "bot");
            addMessage(formatVerifyResult(result), "bot");
            idCardUrl = null;
          }, 3000);
        } else {
          updateVerificationStatus("ກຳລັງຢັ້ງຢືນ...", "verifying", similarity);
          verificationMessage.textContent = `ຄວາມຄ້າຍຄືກັນ: ${(
            similarity * 100
          ).toFixed(1)}% - ກະລຸນາປັບມຸມເບິ່ງ`;
        }
      }
    })
    .catch((error) => {
      console.error("Send frame error:", error);
    });
}

function stopRealtimeVerification() {
  console.log("Stopping realtime verification...");
  isRealtimeVerifying = false;

  // Dừng interval
  if (verificationInterval) {
    clearInterval(verificationInterval);
    verificationInterval = null;
  }

  // Ngắt kết nối WebSocket
  fetch("/stop-websocket-verification", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  }).catch((error) => {
    console.error("Error stopping WebSocket:", error);
  });

  // Reset UI
  startVerifyBtn.style.display = "inline-block";
  stopVerifyBtn.style.display = "none";
  realtimeResult.style.display = "none";

  updateVerificationStatus("ໄດ້ຢຸດການຢັ້ງຢືນແລ້ວ", "verifying", 0);
}

function performRealtimeVerification() {
  if (!isRealtimeVerifying || !cameraVideo.videoWidth) {
    return;
  }

  // Chụp frame từ video
  const context = cameraCanvas.getContext("2d");
  cameraCanvas.width = cameraVideo.videoWidth;
  cameraCanvas.height = cameraVideo.videoHeight;
  context.drawImage(cameraVideo, 0, 0);

  // Chuyển đổi thành blob
  cameraCanvas.toBlob(
    (blob) => {
      // Upload frame để xác thực
      const formData = new FormData();
      formData.append("file", blob, "frame.jpg");

      fetch("/upload", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            // Gọi API xác thực realtime
            fetch("/verify-face-realtime", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                id_card_image_url: idCardUrl,
                selfie_image_url: data.image_url,
              }),
            })
              .then((response) => response.json())
              .then((verifyData) => {
                if (verifyData.success) {
                  const result = verifyData.result;
                  const similarity = result.similarity || 0;
                  const isMatch = result.same_person === true;

                  // Cập nhật UI
                  if (isMatch && similarity > 0.8) {
                    updateVerificationStatus(
                      "ຢັ້ງຢືນສຳເລັດ!",
                      "success",
                      similarity
                    );
                    verificationMessage.textContent =
                      "ໃບໜ້າຖືກຢັ້ງຢືນສຳເລັດແລ້ວ!";

                    // Tự động dừng sau 3 giây
                    setTimeout(() => {
                      stopRealtimeVerification();
                      closeCameraModal();
                      addMessage("ຢັ້ງຢືນໃບໜ້າສຳເລັດ!", "bot");
                      addMessage(formatVerifyResult(result), "bot");
                      idCardUrl = null;
                    }, 3000);
                  } else {
                    updateVerificationStatus(
                      "ກຳລັງຢັ້ງຢືນ...",
                      "verifying",
                      similarity
                    );
                    verificationMessage.textContent = `ຄວາມຄ້າຍຄືກັນ: ${(
                      similarity * 100
                    ).toFixed(1)}% - ກະລຸນາປັບມຸມເບິ່ງ`;
                  }
                } else {
                  updateVerificationStatus("ຂໍ້ຜິດພາດການຢັ້ງຢືນ", "failed", 0);
                  verificationMessage.textContent = "ຂໍ້ຜິດພາດເວລາຢັ້ງຢືນໃບໜ້າ";
                }
              })
              .catch((error) => {
                console.error("Realtime verification error:", error);
                updateVerificationStatus("ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່", "failed", 0);
                verificationMessage.textContent =
                  "ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່ຫາ server";
              });
          }
        })
        .catch((error) => {
          console.error("Upload frame error:", error);
        });
    },
    "image/jpeg",
    0.8
  );
}

function updateVerificationStatus(status, type, similarity) {
  verificationStatus.textContent = status;
  verificationStatus.className = `status-text status-${type}`;

  const similarityPercent = Math.round(similarity * 100);
  similarityFill.style.width = `${similarityPercent}%`;
  similarityText.textContent = `${similarityPercent}%`;
}

function retakePhoto() {
  cameraPreview.style.display = "none";
  cameraVideo.style.display = "block";
  captureBtn.style.display = "inline-block";
  retakeBtn.style.display = "none";
  capturedImageData = null;
}

function verifyFaceFromCamera() {
  if (!capturedImageData) {
    addMessage("ບໍ່ມີຂໍ້ມູນຮູບເພື່ອຢັ້ງຢືນ", "bot");
    return;
  }

  // Nếu không có id_card_url (test mode), chỉ upload ảnh
  if (!idCardUrl) {
    cameraLoading.style.display = "block";
    cameraPreview.style.display = "none";

    const formData = new FormData();
    formData.append("file", capturedImageData, "selfie.jpg");

    fetch("/upload", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        cameraLoading.style.display = "none";

        if (data.success) {
          closeCameraModal();
          addMessage("ທົດສອບກ້ອງສຳເລັດ! ຮູບໄດ້ອັບໂຫຼດແລ້ວ.", "bot");
          addMessage(`URL ຮູບ: ${data.image_url}`, "bot");
        } else {
          addMessage("ຂໍ້ຜິດພາດເວລາອັບໂຫຼດຮູບ: " + data.error, "bot");
          cameraPreview.style.display = "block";
        }
      })
      .catch((error) => {
        cameraLoading.style.display = "none";
        addMessage("ຂໍ້ຜິດພາດເວລາອັບໂຫຼດຮູບ: " + error.message, "bot");
        cameraPreview.style.display = "block";
      });
    return;
  }

  // Xác thực khuôn mặt với id_card_url
  cameraLoading.style.display = "block";
  cameraPreview.style.display = "none";

  const formData = new FormData();
  formData.append("file", capturedImageData, "selfie.jpg");

  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      cameraLoading.style.display = "none";

      if (data.success) {
        // Close camera modal
        closeCameraModal();

        // Verify face
        addMessage("ກຳລັງຢັ້ງຢືນໃບໜ້າ...", "bot");

        fetch("/verify-face", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id_card_image_url: idCardUrl,
            selfie_image_url: data.image_url,
          }),
        })
          .then((response) => response.json())
          .then((verifyData) => {
            if (verifyData.success) {
              const result = verifyData.result;

              // Kiểm tra kết quả xác thực
              if (result.status === "success" && result.same_person === true) {
                addMessage("ຢັ້ງຢືນໃບໜ້າສຳເລັດ!", "bot");
                addMessage(formatVerifyResult(result), "bot");
              } else {
                addMessage("ຢັ້ງຢືນໃບໜ້າບໍ່ສຳເລັດ!", "bot");
                addMessage(formatVerifyResult(result), "bot");

                // Thêm nút xác thực lại
                addRetryVerificationButton();
              }
            } else {
              addMessage("ຢັ້ງຢືນໃບໜ້າບໍ່ສຳເລັດ: " + verifyData.error, "bot");

              // Kiểm tra xem có require_retry không
              if (verifyData.require_retry) {
                addRetryVerificationButton();
              }
            }
            idCardUrl = null;
          })
          .catch((error) => {
            addMessage("ຂໍ້ຜິດພາດເວລາຢັ້ງຢືນໃບໜ້າ: " + error.message, "bot");
            idCardUrl = null;
          });
      } else {
        addMessage("ຂໍ້ຜິດພາດເວລາອັບໂຫຼດຮູບ: " + data.error, "bot");
        cameraPreview.style.display = "block";
      }
    })
    .catch((error) => {
      cameraLoading.style.display = "none";
      addMessage("ຂໍ້ຜິດພາດເວລາອັບໂຫຼດຮູບ: " + error.message, "bot");
      cameraPreview.style.display = "block";
    });
}

function closeCameraModal() {
  cameraModal.style.display = "none";

  // Dừng realtime verification nếu đang chạy
  if (isRealtimeVerifying) {
    stopRealtimeVerification();
  }

  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }

  capturedImageData = null;
  idCardUrl = null;
  isRealtimeVerifying = false;

  cameraVideo.style.display = "block";
  realtimeResult.style.display = "none";
  cameraLoading.style.display = "none";
  startVerifyBtn.style.display = "inline-block";
  stopVerifyBtn.style.display = "none";
}

function handleModalFileSelect(e) {
  const file = e.target.files[0];
  if (file) {
    handleModalFile(file);
  }
}

function handleModalFile(file) {
  // Validate file type
  const allowedTypes = [
    "image/png",
    "image/jpg",
    "image/jpeg",
    "image/gif",
    "image/bmp",
    "image/webp",
  ];
  if (!allowedTypes.includes(file.type)) {
    showError("ຮູບແບບໄຟລ໌ບໍ່ຮອງຮັບ. ກະລຸນາເລືອກໄຟລ໌ຮູບ.");
    return;
  }

  // Validate file size (16MB)
  const maxSize = 16 * 1024 * 1024;
  if (file.size > maxSize) {
    showError("ໄຟລ໌ໃຫຍ່ເກີນໄປ. ກະລຸນາເລືອກໄຟລ໌ນ້ອຍກວ່າ 16MB.");
    return;
  }

  modalSelectedFile = file;
  showModalPreview(file);
}

function showModalPreview(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    modalPreviewImage.src = e.target.result;
    modalFileName.textContent = file.name;
    modalFileSize.textContent = formatFileSize(file.size);

    modalUploadArea.style.display = "none";
    modalPreview.style.display = "block";
  };
  reader.readAsDataURL(file);
}

function processModalImage() {
  if (!modalSelectedFile) return;

  // Show loading
  modalLoading.style.display = "block";
  modalPreview.style.display = "none";

  // Create FormData
  const formData = new FormData();
  formData.append("file", modalSelectedFile);

  // Send to server
  fetch("/upload", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      modalLoading.style.display = "none";

      if (data.success) {
        // Close modal
        closeUploadModal();

        // Kiểm tra xem có phải upload selfie không
        if (idCardUrl) {
          // Upload selfie để xác thực khuôn mặt
          addMessage("ອັບໂຫຼດຮູບ selfie ສຳເລັດ! ກຳລັງຢັ້ງຢືນໃບໜ້າ...", "bot");

          // Gọi API xác thực khuôn mặt
          fetch("/verify-face", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              id_card_image_url: idCardUrl,
              selfie_image_url: data.image_url,
            }),
          })
            .then((response) => response.json())
            .then((verifyData) => {
              if (verifyData.success) {
                addMessage("ຢັ້ງຢືນໃບໜ້າສຳເລັດ!", "bot");
                addMessage(formatVerifyResult(verifyData.result), "bot");
              } else {
                addMessage("ຢັ້ງຢືນໃບໜ້າບໍ່ສຳເລັດ: " + verifyData.error, "bot");
              }
              idCardUrl = null; // Reset
            })
            .catch((error) => {
              addMessage("ຂໍ້ຜິດພາດເວລາຢັ້ງຢືນໃບໜ້າ: " + error.message, "bot");
              idCardUrl = null; // Reset
            });
        } else {
          // Upload căn cước công dân
          addMessage(
            data.message || "ອັບໂຫຼດ ແລະ ປຸງແຕ່ງຮູບບັດປະຈໍາຕົວສຳເລັດ!",
            "bot"
          );

          // Hiển thị thông tin đã format đẹp mắt
          if (data.formatted_html) {
            addMessage(data.formatted_html, "bot");
          } else {
            // Fallback nếu không có formatted_html
            addMessage(formatScanResult(data.scan_result), "bot");
          }

          // Xử lý AI response từ upload (có thể chứa tool calls)
          if (data.ai_response) {
            if (data.ai_response.tool_calls) {
              // AI đã gọi tool để thực hiện bước tiếp theo
              handleToolCalls(data.ai_response.tool_calls);
            } else if (data.ai_response.response) {
              // AI trả lời text
              addMessage(
                formatChatbotResponse(data.ai_response.response),
                "bot"
              );
            }
          }
        }
      } else {
        showError(data.error || "ມີຂໍ້ຜິດພາດເກີດຂຶ້ນໃນການປຸງແຕ່ງຮູບ");
        modalPreview.style.display = "block";
      }
    })
    .catch((error) => {
      modalLoading.style.display = "none";
      modalPreview.style.display = "block";
      showError("ຂໍ້ຜິດພາດການເຊື່ອມຕໍ່: " + error.message);
    });
}

function cancelModalUpload() {
  closeUploadModal();
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  console.log("ລະບົບ eKYC ພ້ອມແລ້ວ!");
});

// Error Handling
function showError(message) {
  // Create error notification
  const errorDiv = document.createElement("div");
  errorDiv.className = "error-notification";
  errorDiv.innerHTML = `
        <div class="error-content">
            <i class="fas fa-exclamation-triangle"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;

  // Add styles for error notification
  errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #dc3545;
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideInRight 0.3s ease;
    `;

  document.body.appendChild(errorDiv);

  // Auto remove after 5 seconds
  setTimeout(() => {
    if (errorDiv.parentElement) {
      errorDiv.remove();
    }
  }, 5000);
}

// Add CSS for error notification animation
const style = document.createElement("style");
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    .error-content {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .error-content button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 5px;
        border-radius: 3px;
    }
    
    .error-content button:hover {
        background: rgba(255,255,255,0.2);
    }
`;
document.head.appendChild(style);

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  console.log("Hệ thống eKYC đã sẵn sàng!");
});

// Test function để kiểm tra camera modal
function testCameraModal() {
  console.log("Testing camera modal...");
  console.log("cameraModal:", cameraModal);
  console.log("cameraVideo:", cameraVideo);
  console.log("cameraMessage:", cameraMessage);

  if (cameraModal) {
    cameraModal.style.display = "flex";
    console.log("Camera modal should be visible now");
  } else {
    console.error("Camera modal element not found!");
  }
}

// Thêm test function vào window để có thể gọi từ console
window.testCameraModal = testCameraModal;
