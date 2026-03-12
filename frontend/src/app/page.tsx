"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";

export default function Home() {
  const catRef = useRef<SVGSVGElement>(null);
  const butterflyRef = useRef<HTMLDivElement>(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const posRef = useRef({ x: 0, y: 0 });
  const velocityRef = useRef({ x: 0, y: 0 });
  const timeRef = useRef<HTMLDivElement>(null);
  const headPosRef = useRef(0);
  const isShrunkRef = useRef(false);
  const shrinkTimeRef = useRef(0);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    };
    window.addEventListener("mousemove", handleMouseMove);
    
    const updateTime = () => {
      if (timeRef.current) {
        const now = new Date();
        timeRef.current.textContent = now.toLocaleTimeString("en-US", { 
          hour12: false, 
          hour: "2-digit", 
          minute: "2-digit", 
          second: "2-digit" 
        });
      }
    };
    const timeInterval = setInterval(updateTime, 1000);
    updateTime();

    let animationId: number;
    let lastTime = performance.now();

    const animate = (currentTime: number) => {
      const deltaTime = (currentTime - lastTime) / 1000;
      lastTime = currentTime;

      const mouse = mouseRef.current;
      const pos = posRef.current;
      const velocity = velocityRef.current;

      const targetX = mouse.x;
      const targetY = mouse.y;
      const dx = targetX - pos.x;
      const dy = targetY - pos.y;
      
      velocity.x += dx * 0.08 * deltaTime * 60;
      velocity.y += dy * 0.08 * deltaTime * 60;
      
      velocity.x *= 0.85;
      velocity.y *= 0.85;
      
      const wobble = Math.sin(currentTime * 0.01) * 3;
      pos.x += velocity.x * deltaTime * 60 + wobble;
      pos.y += velocity.y * deltaTime * 60;

      if (butterflyRef.current) {
        butterflyRef.current.style.left = (pos.x - 12) + "px";
        butterflyRef.current.style.top = (pos.y - 12) + "px";
      }

      if (catRef.current) {
        const catCenterX = window.innerWidth / 2;
        const catCenterY = window.innerHeight / 2;
        
        const eyeAngle = Math.atan2(pos.y - catCenterY, pos.x - catCenterX);
        const eyeRadius = 3;
        
        const leftEye = catRef.current.querySelector("#left-pupil") as SVGCircleElement;
        const rightEye = catRef.current.querySelector("#right-pupil") as SVGCircleElement;
        
        if (leftEye && rightEye) {
          const pupilX = Math.cos(eyeAngle) * eyeRadius;
          const pupilY = Math.sin(eyeAngle) * eyeRadius;
          leftEye.setAttribute("cx", (80 + pupilX).toString());
          leftEye.setAttribute("cy", (75 + pupilY).toString());
          rightEye.setAttribute("cx", (120 + pupilX).toString());
          rightEye.setAttribute("cy", (75 + pupilY).toString());
        }

        const head = catRef.current.querySelector("#cat-head") as SVGGElement;
        const leftEar = catRef.current.querySelector("#left-ear") as SVGPathElement;
        const rightEar = catRef.current.querySelector("#right-ear") as SVGPathElement;
        
        if (head) {
          const dist = Math.sqrt(
            Math.pow(pos.x - catCenterX, 2) + Math.pow(pos.y - catCenterY, 2)
          );
          
          if (dist < 150 && !isShrunkRef.current) {
            isShrunkRef.current = true;
            shrinkTimeRef.current = currentTime;
          }
          
          if (isShrunkRef.current) {
            const shrinkDuration = 300;
            const elapsed = currentTime - shrinkTimeRef.current;
            
            if (elapsed < shrinkDuration) {
              const progress = elapsed / shrinkDuration;
              const easeOut = 1 - Math.pow(1 - progress, 3);
              headPosRef.current = 30 * (1 - easeOut);
              
              if (leftEar) {
                leftEar.setAttribute("transform", "translate(0, " + (headPosRef.current + 5) + ")");
              }
              if (rightEar) {
                rightEar.setAttribute("transform", "translate(0, " + (headPosRef.current + 5) + ")");
              }
            } else if (dist >= 150) {
              isShrunkRef.current = false;
            }
          } else if (headPosRef.current > 0) {
            headPosRef.current = Math.max(0, headPosRef.current - 2);
            head.setAttribute("transform", "translate(0, " + headPosRef.current + ")");
            if (leftEar) leftEar.setAttribute("transform", "translate(0, " + (headPosRef.current + 5) + ")");
            if (rightEar) rightEar.setAttribute("transform", "translate(0, " + (headPosRef.current + 5) + ")");
          }
        }
      }

      animationId = requestAnimationFrame(animate);
    };

    animationId = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      clearInterval(timeInterval);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <main className="fixed inset-0 bg-black overflow-hidden cursor-none">
      <div 
        ref={timeRef}
        className="absolute top-8 left-1/2 -translate-x-1/2 text-[#333] text-xl font-light tracking-[0.3em]"
      />
      
      <div 
        ref={butterflyRef}
        className="fixed w-6 h-6 pointer-events-none z-50"
        style={{ transition: "left 0.1s ease-out, top 0.1s ease-out" }}
      >
        <svg viewBox="0 0 24 24" className="w-full h-full">
          <path 
            d="M12 2C12 2 8 6 8 12C8 14 10 16 12 18C14 16 12 14 12 12C12 14 10 16 12 18C14 16 12 14 16 12C16 6 12 2 12 2Z" 
            fill="none" 
            stroke="#fff" 
            strokeWidth="1"
          >
            <animate 
              attributeName="d" 
              dur="0.2s" 
              repeatCount="indefinite"
              values="M12 2C12 2 8 6 8 12C8 14 10 16 12 18C14 16 12 14 12 12C12 14 10 16 12 18C14 16 12 14 16 12C16 6 12 2 12 2Z;M12 2C12 2 6 8 6 12C6 14 8 16 12 18C16 14 14 14 12 12C12 14 8 16 12 18C16 14 14 14 14 14C14 8 12 2 12 2Z;M12 2C12 2 8 6 8 12C8 14 10 16 12 18C14 16 12 14 12 12C12 14 10 16 12 18C14 16 12 14 16 12C16 6 12 2 12 2Z"
            />
          </path>
        </svg>
      </div>

      <svg
        ref={catRef}
        viewBox="0 0 200 180"
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[360px]"
        style={{ stroke: "#fff", strokeWidth: 1.5, fill: "none", strokeLinecap: "round", strokeLinejoin: "round" }}
      >
        <g id="cat-head">
          <path id="left-ear" d="M50 40 L35 5 L70 25" />
          <path id="right-ear" d="M150 40 L165 5 L130 25" />
          <ellipse cx="100" cy="90" rx="60" ry="50" />
          <ellipse cx="70" cy="85" rx="18" ry="15" fill="#000" stroke="none" />
          <ellipse cx="130" cy="85" rx="18" ry="15" fill="#000" stroke="none" />
          <circle id="left-pupil" cx="80" cy="75" r="3" fill="#fff" stroke="none" />
          <circle id="right-pupil" cx="120" cy="75" r="3" fill="#fff" stroke="none" />
          <ellipse cx="100" cy="105" rx="8" ry="5" />
          <path d="M92 115 L100 125 L108 115" />
          <path d="M45 75 Q35 85 45 95" />
          <path d="M155 75 Q165 85 155 95" />
        </g>
      </svg>

      <Link 
        href="/dashboard"
        className="absolute bottom-8 left-1/2 -translate-x-1/2 text-[#222] text-sm hover:text-[#444]"
      >
        Enter
      </Link>
    </main>
  );
}
