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

// Chat Form Events
chatForm.addEventListener("submit", handleSubmit);
uploadBtn.addEventListener("click", () =>
    openUploadModal("Vui lòng upload ảnh căn cước công dân của bạn")
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
                "Đây là test camera modal. Hãy chụp ảnh để test tính năng camera.",
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

    // Send to server
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
                addMessage("Lỗi: " + (data.error || "Có lỗi xảy ra"), "bot");
            }
        })
        .catch((error) => {
            hideTypingIndicator();
            addMessage("Lỗi kết nối: " + error.message, "bot");
        });
}

function addRetryVerificationButton() {
    const retryButton = document.createElement("div");
    retryButton.className = "retry-verification-btn";
    retryButton.innerHTML = `
    <button class="btn btn-warning" onclick="retryVerification()">
      <i class="fas fa-redo"></i> Xác thực lại
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
    addMessage("Vui lòng xác thực lại khuôn mặt bằng camera", "bot");

    // Tìm lại id_card_url từ conversation history
    // Tạm thời sử dụng một URL test - trong thực tế sẽ lấy từ conversation
    const testIdCardUrl = "https://example.com/test-id-card.jpg";

    setTimeout(() => {
        openCameraRealtimeModal(
            "Hãy chụp ảnh selfie để xác thực lại khuôn mặt",
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
    if (!scanResult) return "<p>Không có dữ liệu</p>";

    let html = '<div class="scan-result">';

    if (scanResult.text) {
        html += `<h4><i class="fas fa-text-width"></i> Văn bản trích xuất:</h4>`;
        html += `<p class="extracted-text">${scanResult.text}</p>`;
    }

    if (scanResult.document_type) {
        html += `<h4><i class="fas fa-id-card"></i> Loại tài liệu:</h4>`;
        html += `<p class="document-type">${scanResult.document_type}</p>`;
    }

    if (scanResult.display_name) {
        html += `<h4><i class="fas fa-user"></i> Tên hiển thị:</h4>`;
        html += `<p class="display-name">${scanResult.display_name}</p>`;
    }

    // Add other fields if they exist
    Object.keys(scanResult).forEach((key) => {
        if (
            !["text", "document_type", "display_name", "img_base64"].includes(
                key
            )
        ) {
            html += `<h4><i class="fas fa-info-circle"></i> ${key}:</h4>`;
            html += `<p>${scanResult[key]}</p>`;
        }
    });

    html += "</div>";
    return html;
}

function formatMarkdownToHtml(markdownText) {
    if (!markdownText) return "<p>Không có nội dung</p>";

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
    if (!responseText) return "<p>Không có phản hồi</p>";

    // Check if it's already HTML
    if (responseText.trim().startsWith("<")) {
        return responseText;
    }

    // Convert Markdown to HTML
    return formatMarkdownToHtml(responseText);
}

function formatVerifyResult(verifyResult) {
    if (!verifyResult) return "<p>Không có dữ liệu xác thực</p>";

    let html = '<div class="verify-result">';

    // Xử lý format mới từ WebSocket API
    if (verifyResult.status === "success") {
        html += `<h4><i class="fas fa-check-circle"></i> Trạng thái:</h4>`;
        html += `<p class="match-success">Xác thực thành công</p>`;

        if (verifyResult.same_person !== undefined) {
            const matchStatus = verifyResult.same_person
                ? "Cùng một người"
                : "Không cùng người";
            const matchClass = verifyResult.same_person
                ? "match-success"
                : "match-fail";
            html += `<h4><i class="fas fa-user-check"></i> Kết quả:</h4>`;
            html += `<p class="${matchClass}">${matchStatus}</p>`;
        }

        if (verifyResult.similarity !== undefined) {
            html += `<h4><i class="fas fa-percentage"></i> Độ tương đồng:</h4>`;
            html += `<p class="match-score">${(
                verifyResult.similarity * 100
            ).toFixed(2)}%</p>`;
        }

        if (verifyResult.msg) {
            html += `<h4><i class="fas fa-comment"></i> Thông báo:</h4>`;
            html += `<p>${verifyResult.msg}</p>`;
        }
    } else {
        html += `<h4><i class="fas fa-times-circle"></i> Trạng thái:</h4>`;
        html += `<p class="match-fail">Xác thực thất bại</p>`;

        if (verifyResult.msg) {
            html += `<h4><i class="fas fa-exclamation-triangle"></i> Lỗi:</h4>`;
            html += `<p>${verifyResult.msg}</p>`;
        }
    }

    // Xử lý format cũ (backward compatibility)
    if (verifyResult.match_score !== undefined) {
        html += `<h4><i class="fas fa-percentage"></i> Điểm khớp:</h4>`;
        html += `<p class="match-score">${(
            verifyResult.match_score * 100
        ).toFixed(2)}%</p>`;
    }

    if (verifyResult.is_match !== undefined) {
        const matchStatus = verifyResult.is_match ? "Khớp" : "Không khớp";
        const matchClass = verifyResult.is_match
            ? "match-success"
            : "match-fail";
        html += `<h4><i class="fas fa-check-circle"></i> Kết quả:</h4>`;
        html += `<p class="${matchClass}">${matchStatus}</p>`;
    }

    if (verifyResult.confidence !== undefined) {
        html += `<h4><i class="fas fa-chart-line"></i> Độ tin cậy:</h4>`;
        html += `<p class="confidence">${(
            verifyResult.confidence * 100
        ).toFixed(2)}%</p>`;
    }

    // Add other fields if they exist
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
                "Không thể truy cập camera. Vui lòng kiểm tra quyền truy cập camera.",
                "bot"
            );
            closeCameraModal();
        });
}

function startRealtimeVerification() {
    console.log("Starting realtime verification, idCardUrl:", idCardUrl); // Debug log

    if (!idCardUrl) {
        addMessage("Không có URL ảnh căn cước để xác thực", "bot");
        return;
    }

    console.log("Starting realtime verification...");
    isRealtimeVerifying = true;

    // Hiển thị UI realtime
    startVerifyBtn.style.display = "none";
    stopVerifyBtn.style.display = "inline-block";
    realtimeResult.style.display = "block";

    // Reset UI
    updateVerificationStatus("Đang kết nối...", "verifying", 0);
    verificationMessage.textContent = "Đang kết nối đến server xác thực";

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
                updateVerificationStatus("Đang xác thực...", "verifying", 0);
                verificationMessage.textContent =
                    "Vui lòng nhìn thẳng vào camera";

                // Bắt đầu gửi frame
                startFrameCapture();
            } else {
                updateVerificationStatus("Lỗi kết nối", "failed", 0);
                verificationMessage.textContent =
                    "Không thể kết nối đến server: " + data.error;
            }
        })
        .catch((error) => {
            console.error("WebSocket connection error:", error);
            updateVerificationStatus("Lỗi kết nối", "failed", 0);
            verificationMessage.textContent = "Lỗi kết nối đến server";
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
        const frameBase64 = cameraCanvas
            .toDataURL("image/jpeg", 0.8)
            .split(",")[1];

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
                    updateVerificationStatus(
                        "Xác thực thành công!",
                        "success",
                        similarity
                    );
                    verificationMessage.textContent =
                        "Khuôn mặt đã được xác thực thành công!";

                    // Tự động dừng sau 3 giây
                    setTimeout(() => {
                        stopRealtimeVerification();
                        closeCameraModal();
                        addMessage("Xác thực khuôn mặt thành công!", "bot");
                        addMessage(formatVerifyResult(result), "bot");
                        idCardUrl = null;
                    }, 3000);
                } else {
                    updateVerificationStatus(
                        "Đang xác thực...",
                        "verifying",
                        similarity
                    );
                    verificationMessage.textContent = `Độ tương đồng: ${(
                        similarity * 100
                    ).toFixed(1)}% - Vui lòng điều chỉnh góc nhìn`;
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

    updateVerificationStatus("Đã dừng xác thực", "verifying", 0);
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
                                            "Xác thực thành công!",
                                            "success",
                                            similarity
                                        );
                                        verificationMessage.textContent =
                                            "Khuôn mặt đã được xác thực thành công!";

                                        // Tự động dừng sau 3 giây
                                        setTimeout(() => {
                                            stopRealtimeVerification();
                                            closeCameraModal();
                                            addMessage(
                                                "Xác thực khuôn mặt thành công!",
                                                "bot"
                                            );
                                            addMessage(
                                                formatVerifyResult(result),
                                                "bot"
                                            );
                                            idCardUrl = null;
                                        }, 3000);
                                    } else {
                                        updateVerificationStatus(
                                            "Đang xác thực...",
                                            "verifying",
                                            similarity
                                        );
                                        verificationMessage.textContent = `Độ tương đồng: ${(
                                            similarity * 100
                                        ).toFixed(
                                            1
                                        )}% - Vui lòng điều chỉnh góc nhìn`;
                                    }
                                } else {
                                    updateVerificationStatus(
                                        "Lỗi xác thực",
                                        "failed",
                                        0
                                    );
                                    verificationMessage.textContent =
                                        "Lỗi khi xác thực khuôn mặt";
                                }
                            })
                            .catch((error) => {
                                console.error(
                                    "Realtime verification error:",
                                    error
                                );
                                updateVerificationStatus(
                                    "Lỗi kết nối",
                                    "failed",
                                    0
                                );
                                verificationMessage.textContent =
                                    "Lỗi kết nối đến server";
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
        addMessage("Không có dữ liệu ảnh để xác thực", "bot");
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
                    addMessage(
                        "Test camera thành công! Ảnh đã được upload.",
                        "bot"
                    );
                    addMessage(`URL ảnh: ${data.image_url}`, "bot");
                } else {
                    addMessage("Lỗi khi upload ảnh: " + data.error, "bot");
                    cameraPreview.style.display = "block";
                }
            })
            .catch((error) => {
                cameraLoading.style.display = "none";
                addMessage("Lỗi khi upload ảnh: " + error.message, "bot");
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
                addMessage("Đang xác thực khuôn mặt...", "bot");

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
                            if (
                                result.status === "success" &&
                                result.same_person === true
                            ) {
                                addMessage(
                                    "Xác thực khuôn mặt thành công!",
                                    "bot"
                                );
                                addMessage(formatVerifyResult(result), "bot");
                            } else {
                                addMessage(
                                    "Xác thực khuôn mặt thất bại!",
                                    "bot"
                                );
                                addMessage(formatVerifyResult(result), "bot");

                                // Thêm nút xác thực lại
                                addRetryVerificationButton();
                            }
                        } else {
                            addMessage(
                                "Xác thực khuôn mặt thất bại: " +
                                    verifyData.error,
                                "bot"
                            );

                            // Kiểm tra xem có require_retry không
                            if (verifyData.require_retry) {
                                addRetryVerificationButton();
                            }
                        }
                        idCardUrl = null;
                    })
                    .catch((error) => {
                        addMessage(
                            "Lỗi khi xác thực khuôn mặt: " + error.message,
                            "bot"
                        );
                        idCardUrl = null;
                    });
            } else {
                addMessage("Lỗi khi upload ảnh: " + data.error, "bot");
                cameraPreview.style.display = "block";
            }
        })
        .catch((error) => {
            cameraLoading.style.display = "none";
            addMessage("Lỗi khi upload ảnh: " + error.message, "bot");
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
        showError("Định dạng file không được hỗ trợ. Vui lòng chọn file ảnh.");
        return;
    }

    // Validate file size (16MB)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showError("File quá lớn. Vui lòng chọn file nhỏ hơn 16MB.");
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
                    addMessage(
                        "Tôi đã upload ảnh selfie thành công! Đang xác thực khuôn mặt...",
                        "bot"
                    );

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
                                addMessage(
                                    "Xác thực khuôn mặt thành công!",
                                    "bot"
                                );
                                addMessage(
                                    formatVerifyResult(verifyData.result),
                                    "bot"
                                );
                            } else {
                                addMessage(
                                    "Xác thực khuôn mặt thất bại: " +
                                        verifyData.error,
                                    "bot"
                                );
                            }
                            idCardUrl = null; // Reset
                        })
                        .catch((error) => {
                            addMessage(
                                "Lỗi khi xác thực khuôn mặt: " + error.message,
                                "bot"
                            );
                            idCardUrl = null; // Reset
                        });
                } else {
                    // Upload căn cước công dân
                    addMessage(
                        data.message ||
                            "Tôi đã upload và xử lý ảnh căn cước công dân thành công!",
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
                                formatChatbotResponse(
                                    data.ai_response.response
                                ),
                                "bot"
                            );
                        }
                    }
                }
            } else {
                showError(data.error || "Có lỗi xảy ra khi xử lý ảnh");
                modalPreview.style.display = "block";
            }
        })
        .catch((error) => {
            modalLoading.style.display = "none";
            modalPreview.style.display = "block";
            showError("Lỗi kết nối: " + error.message);
        });
}

function cancelModalUpload() {
    closeUploadModal();
}

// Initialize
document.addEventListener("DOMContentLoaded", () => {
    console.log("Hệ thống eKYC đã sẵn sàng!");
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
