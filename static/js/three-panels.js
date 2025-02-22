class PanelScene {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.panels = new Map();
        this.init();
    }

    init() {
        // Configurar renderer
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x000000, 0);
        this.renderer.domElement.style.pointerEvents = 'none'; // Importante: permite clicks a través del canvas
        document.body.appendChild(this.renderer.domElement);
        
        // Posicionar cámara
        this.camera.position.z = 5;
        
        // Agregar luz
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.2);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.3);
        directionalLight.position.set(0, 1, 2);
        this.scene.add(directionalLight);
        
        // Event listener para resize
        window.addEventListener('resize', () => this.onWindowResize(), false);
        
        this.animate();
    }

    createPanel(element, index) {
        const geometry = new THREE.BoxGeometry(1, 0.8, 0.05);
        const material = new THREE.MeshPhongMaterial({
            color: 0x2196F3,
            transparent: true,
            opacity: 0.2,
            side: THREE.DoubleSide,
            specular: 0x444444,
            shininess: 30
        });
        
        const panel = new THREE.Mesh(geometry, material);
        
        // Posicionar panel
        const row = Math.floor(index / 2);
        const col = index % 2;
        panel.position.x = col * 2 - 1;
        panel.position.y = -row * 1.2 + 1;
        panel.position.z = 0;
        
        this.scene.add(panel);
        this.panels.set(element, panel);
        
        return panel;
    }

    expandPanel(element) {
        const panel = this.panels.get(element);
        if (!panel) return;
        
        gsap.to(panel.scale, {
            x: 1.5,
            y: 1.5,
            z: 1.5,
            duration: 0.5,
            ease: "power2.out"
        });
        
        gsap.to(panel.position, {
            z: 0.5,
            duration: 0.5,
            ease: "power2.out"
        });

        gsap.to(panel.material, {
            opacity: 0.4,
            duration: 0.5
        });
    }

    contractPanel(element) {
        const panel = this.panels.get(element);
        if (!panel) return;
        
        gsap.to(panel.scale, {
            x: 1,
            y: 1,
            z: 1,
            duration: 0.5,
            ease: "power2.in"
        });
        
        gsap.to(panel.position, {
            z: 0,
            duration: 0.5,
            ease: "power2.in"
        });

        gsap.to(panel.material, {
            opacity: 0.2,
            duration: 0.5
        });
    }

    onWindowResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Rotación suave de los paneles
        this.panels.forEach(panel => {
            panel.rotation.y += 0.001;
        });
        
        this.renderer.render(this.scene, this.camera);
    }
} 