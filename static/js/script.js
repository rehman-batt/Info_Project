document.getElementById('generateKeys').onclick = async () => {
    const response = await fetch('/generate_keys', { method: 'POST' });
    const result = await response.json();

    if (result.error) {
        document.getElementById('outputBox').textContent = `❌ Error: ${result.error}`;
    } else {
        document.getElementById('outputBox').textContent =
            `✅ Keys Generated\n\nPublic Key:\n${result.public_key}\n\nPrivate Key:\n${result.private_key}`;
    }
};

document.getElementById('encryptBtn').onclick = async () => {
    const text = document.getElementById('textInput').value;
    const response = await fetch('/encrypt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    const result = await response.json();

    if (result.error) {
        document.getElementById('outputBox').textContent = `❌ Error: ${result.error}`;
    } else {
        document.getElementById('outputBox').textContent = `🔐 Encrypted Text:\n${result.encrypted}`;
    }
};

document.getElementById('decryptBtn').onclick = async () => {
    const response = await fetch('/decrypt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    const result = await response.json();

    if (result.error) {
        document.getElementById('outputBox').textContent = `❌ Error: ${result.error}`;
    } else {
        document.getElementById('outputBox').textContent = `🔓 Decrypted Text:\n${result.decrypted}`;
    }
};
