import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { AssistantState } from '../types';

interface ThreeAvatarProps {
  state: AssistantState;
  outputVolume: number;
  micVolume: number;
  hologramColor?: string;
  intensity?: number;
}

export const ThreeAvatar: React.FC<ThreeAvatarProps> = ({
  state,
  outputVolume,
  micVolume,
  hologramColor = '#00f0ff',
  intensity = 1.0,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth || 320;
    const height = containerRef.current.clientHeight || 320;

    // 1. Scene setup
    const scene = new THREE.Scene();

    // 2. Camera setup
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 7);

    // 3. Renderer
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    containerRef.current.appendChild(renderer.domElement);

    // 4. Color parsing
    const primaryColor = new THREE.Color(hologramColor);

    // 5. Holographic Avatar Geometry - Holographic Core Head & Torso
    const avatarGroup = new THREE.Group();
    scene.add(avatarGroup);

    // Head sphere / dodecahedron
    const headGeo = new THREE.IcosahedronGeometry(0.85, 3);
    const headMat = new THREE.MeshBasicMaterial({
      color: primaryColor,
      wireframe: true,
      transparent: true,
      opacity: 0.6 * intensity,
    });
    const headMesh = new THREE.Mesh(headGeo, headMat);
    avatarGroup.add(headMesh);

    // Inner Glowing Core
    const coreGeo = new THREE.IcosahedronGeometry(0.5, 2);
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0xffffff,
      transparent: true,
      opacity: 0.85 * intensity,
    });
    const coreMesh = new THREE.Mesh(coreGeo, coreMat);
    headMesh.add(coreMesh);

    // Eyes
    const eyeGeo = new THREE.SphereGeometry(0.08, 12, 12);
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0.95 });
    
    const leftEye = new THREE.Mesh(eyeGeo, eyeMat);
    leftEye.position.set(-0.28, 0.15, 0.72);
    headMesh.add(leftEye);

    const rightEye = new THREE.Mesh(eyeGeo, eyeMat);
    rightEye.position.set(0.28, 0.15, 0.72);
    headMesh.add(rightEye);

    // Holographic Mouth (Lip Sync Scale Bar)
    const mouthGeo = new THREE.BoxGeometry(0.3, 0.04, 0.04);
    const mouthMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.9 });
    const mouthMesh = new THREE.Mesh(mouthGeo, mouthMat);
    mouthMesh.position.set(0, -0.28, 0.75);
    headMesh.add(mouthMesh);

    // Holographic Orbiting Rings (JARVIS Halo Interface)
    const ringGeo1 = new THREE.TorusGeometry(1.4, 0.015, 16, 100);
    const ringMat1 = new THREE.MeshBasicMaterial({ color: primaryColor, transparent: true, opacity: 0.4 });
    const ring1 = new THREE.Mesh(ringGeo1, ringMat1);
    ring1.rotation.x = Math.PI / 3;
    avatarGroup.add(ring1);

    const ringGeo2 = new THREE.TorusGeometry(1.7, 0.01, 16, 100);
    const ringMat2 = new THREE.MeshBasicMaterial({ color: 0x00a8ff, transparent: true, opacity: 0.3 });
    const ring2 = new THREE.Mesh(ringGeo2, ringMat2);
    ring2.rotation.y = Math.PI / 4;
    avatarGroup.add(ring2);

    // Ambient Holographic Floating Particles
    const particleCount = 120;
    const particleGeo = new THREE.BufferGeometry();
    const particlePositions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount * 3; i += 3) {
      particlePositions[i] = (Math.random() - 0.5) * 5;
      particlePositions[i + 1] = (Math.random() - 0.5) * 5;
      particlePositions[i + 2] = (Math.random() - 0.5) * 5;
    }
    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: primaryColor,
      size: 0.04,
      transparent: true,
      opacity: 0.6,
    });
    const particleSystem = new THREE.Points(particleGeo, particleMat);
    scene.add(particleSystem);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    // Mouse Tracking for Head Eyes
    let mouseX = 0;
    let mouseY = 0;
    const handleMouseMove = (e: MouseEvent) => {
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      mouseX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
      mouseY = -((e.clientY - rect.top) / rect.height - 0.5) * 2;
    };
    window.addEventListener('mousemove', handleMouseMove);

    // Animation Loop
    let animationFrameId: number;
    let clock = new THREE.Clock();
    let blinkTimer = 0;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // 1. Idle Breathing & Floating
      avatarGroup.position.y = Math.sin(elapsedTime * 1.5) * 0.12;

      // 2. Smooth Head Movement tracking cursor
      headMesh.rotation.y += (mouseX * 0.4 - headMesh.rotation.y) * 0.05;
      headMesh.rotation.x += (-mouseY * 0.3 - headMesh.rotation.x) * 0.05;

      // 3. Ring Rotations
      ring1.rotation.z += 0.008;
      ring2.rotation.z -= 0.012;
      particleSystem.rotation.y += 0.002;

      // 4. Blinking Logic
      blinkTimer += 0.016;
      if (blinkTimer > 3.5) {
        leftEye.scale.y = 0.1;
        rightEye.scale.y = 0.1;
        if (blinkTimer > 3.65) {
          leftEye.scale.y = 1.0;
          rightEye.scale.y = 1.0;
          blinkTimer = 0;
        }
      }

      // 5. State & Audio Reactive Behaviors (Lip Sync, Thinking, Speaking)
      if (state === 'speaking' || outputVolume > 0.01) {
        const mouthOpen = Math.min(1.0, 0.1 + outputVolume * 4.5);
        mouthMesh.scale.y = 1.0 + mouthOpen * 8.0;
        coreMesh.scale.setScalar(1.0 + outputVolume * 1.2);
        headMat.opacity = Math.min(0.9, 0.6 + outputVolume * 0.5);
      } else {
        mouthMesh.scale.y = 1.0;
        coreMesh.scale.setScalar(1.0);
        headMat.opacity = 0.6 * intensity;
      }

      if (state === 'processing' || state === 'analyzing') {
        headMesh.rotation.z += 0.03;
        coreMat.color.setHex(0xffaa00);
      } else if (state === 'listening') {
        coreMat.color.setHex(0x00ffaa);
        ring1.scale.setScalar(1.0 + micVolume * 1.5);
      } else {
        coreMat.color.setHex(0xffffff);
        ring1.scale.setScalar(1.0);
      }

      renderer.render(scene, camera);
    };

    animate();

    // Resize Handler
    const handleResize = () => {
      if (!containerRef.current) return;
      const w = containerRef.current.clientWidth;
      const h = containerRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [state, hologramColor, intensity]);

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      <div ref={containerRef} className="w-full h-full max-w-[360px] max-h-[360px]" />
      {/* Holographic Scanline Overlay effect */}
      <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-cyan-500/5 to-transparent bg-[length:100%_4px] opacity-40 animate-pulse" />
    </div>
  );
};
