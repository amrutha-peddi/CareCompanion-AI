import { useState, useRef, Suspense } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Points, PointMaterial, Preload } from "@react-three/drei";
import * as random from "maath/random/dist/maath-random.esm";

const Stars = (props) => {
  const ref = useRef();
  const numStars = 2000;
  const [sphere] = useState(() =>
    random.inSphere(new Float32Array(numStars * 3), { radius: 5 }) // bigger radius
  );

  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.y += delta / 10; // rotate slowly
    }
  });

  return (
    <Points ref={ref} positions={sphere} stride={3} frustumCulled {...props}>
      <PointMaterial
        transparent
        color="#f272c8"
        size={0.03}       // visible size
        sizeAttenuation
        depthWrite={false}
      />
    </Points>
  );
};

const StarBackground = () => {
  return (
    <Canvas
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh", // ensure full viewport
        zIndex: -1,
      }}
      camera={{ position: [0, 0, 10] }}
    >
      <Suspense fallback={null}>
        <Stars />
      </Suspense>
      <Preload all />
    </Canvas>
  );
};

export default StarBackground;
