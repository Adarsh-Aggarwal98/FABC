/**
 * SignaturePad — canvas-based e-signature component.
 * No external dependencies required.
 *
 * Props:
 *   onSave(base64String) — called with base64 PNG when user clicks Save
 *   onClear()            — called when cleared
 *   width  (default 400)
 *   height (default 150)
 *   existingSignature    — base64 string to display existing sig
 */
import React, { useRef, useEffect, useState } from 'react';

export default function SignaturePad({
  onSave,
  onClear,
  width = 400,
  height = 150,
  existingSignature = null,
  label = 'Sign here',
}) {
  const canvasRef = useRef(null);
  const [drawing, setDrawing] = useState(false);
  const [hasContent, setHasContent] = useState(false);
  const [saved, setSaved] = useState(false);
  const lastPos = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = '#1A2E5A';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    if (existingSignature) {
      const img = new Image();
      img.onload = () => ctx.drawImage(img, 0, 0);
      img.src = `data:image/png;base64,${existingSignature}`;
      setHasContent(true);
    }
  }, [existingSignature]);

  const getPos = (e, canvas) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    if (e.touches) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY,
      };
    }
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const startDraw = (e) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    setDrawing(true);
    setSaved(false);
    lastPos.current = getPos(e, canvas);
  };

  const draw = (e) => {
    e.preventDefault();
    if (!drawing) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const pos = getPos(e, canvas);
    ctx.beginPath();
    ctx.moveTo(lastPos.current.x, lastPos.current.y);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    lastPos.current = pos;
    setHasContent(true);
  };

  const stopDraw = (e) => {
    e.preventDefault();
    setDrawing(false);
    lastPos.current = null;
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    setHasContent(false);
    setSaved(false);
    onClear?.();
  };

  const handleSave = () => {
    if (!hasContent) return;
    const canvas = canvasRef.current;
    const dataUrl = canvas.toDataURL('image/png');
    const base64 = dataUrl.replace('data:image/png;base64,', '');
    setSaved(true);
    onSave?.(base64);
  };

  return (
    <div className="flex flex-col gap-2">
      <p className="text-xs text-gray-500 font-medium">{label}</p>
      <div
        className="border-2 border-dashed border-gray-300 rounded-lg bg-white overflow-hidden"
        style={{ cursor: 'crosshair', touchAction: 'none' }}
      >
        <canvas
          ref={canvasRef}
          width={width}
          height={height}
          style={{ display: 'block', width: '100%', height: 'auto' }}
          onMouseDown={startDraw}
          onMouseMove={draw}
          onMouseUp={stopDraw}
          onMouseLeave={stopDraw}
          onTouchStart={startDraw}
          onTouchMove={draw}
          onTouchEnd={stopDraw}
        />
      </div>
      <div className="flex gap-2">
        <button
          type="button"
          onClick={handleClear}
          className="px-3 py-1.5 text-xs text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 transition"
        >
          Clear
        </button>
        <button
          type="button"
          onClick={handleSave}
          disabled={!hasContent}
          className={`px-3 py-1.5 text-xs rounded-md font-medium transition ${
            hasContent
              ? 'bg-primary-600 text-white hover:bg-primary-700'
              : 'bg-gray-200 text-gray-400 cursor-not-allowed'
          }`}
        >
          {saved ? 'Signature Saved ✓' : 'Save Signature'}
        </button>
      </div>
    </div>
  );
}
