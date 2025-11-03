// Global variable for the Pi Frame address
const PiFrameAddress = 'https://commonplacely-unforecasted-alica.ngrok-free.dev'; // Update this with your actual server URL

// Prompt submission handler
document.getElementById('submitPromptBtn').addEventListener('click', async () => {
    const promptInput = document.getElementById('promptInput');
    const prompt = promptInput.value.trim();
    
    if (!prompt) {
        alert('Please enter a prompt!');
        return;
    }
    
    try {
        const url = `${PiFrameAddress}/prompt?prompt=${encodeURIComponent(prompt)}`;
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'ngrok-skip-browser-warning': '0123'
            }
        });
        
        if (response.ok) {
            alert('Prompt submitted successfully!');
            promptInput.value = '';
        } else {
            alert('Failed to submit prompt. Please try again.');
        }
    } catch (error) {
        console.error('Error submitting prompt:', error);
        alert('Error submitting prompt. Please check your connection.');
    }
});

// Image upload and preview
const imageInput = document.getElementById('imageInput');
const imagePreview = document.getElementById('imagePreview');
const sendImageBtn = document.getElementById('sendImageBtn');
let selectedImage = null;

imageInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        
        reader.onload = (event) => {
            // Strip data URL prefix (e.g., "data:image/png;base64,") to get just the base64 data
            let base64Data = event.target.result;
            if (base64Data.includes(',')) {
                base64Data = base64Data.split(',')[1];
            }
            
            selectedImage = {
                name: file.name,
                type: file.type,
                size: file.size,
                data: base64Data // Base64 encoded image data (without data URL prefix)
            };
            
            // Display preview
            imagePreview.innerHTML = `<img src="${event.target.result}" alt="Preview">`;
            imagePreview.classList.add('active');
            sendImageBtn.disabled = false;
        };
        
        reader.readAsDataURL(file);
    } else {
        alert('Please select a valid image file!');
    }
});

// Send image handler
sendImageBtn.addEventListener('click', async () => {
    if (!selectedImage) {
        alert('Please select an image first!');
        return;
    }
    
    try {
        const response = await fetch(`${PiFrameAddress}/image`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': '0123'
            },
            body: JSON.stringify(selectedImage),
        });
        
        if (response.ok) {
            alert('Image sent successfully!');
            // Allow user to upload a different image
            imageInput.value = '';
            imagePreview.classList.remove('active');
            imagePreview.innerHTML = '';
            sendImageBtn.disabled = true;
            selectedImage = null;
        } else {
            alert('Failed to send image. Please try again.');
        }
    } catch (error) {
        console.error('Error sending image:', error);
        alert('Error sending image. Please check your connection.');
    }
});

