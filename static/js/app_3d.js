//Variables for setup

let container;
let camera;
let renderer;
let scene;
let house;
let controls;

function init() {
  container = document.querySelector(".scene");

  //Create scene
  scene = new THREE.Scene();

  const fov = 35;
  const aspect = container.clientWidth / container.clientHeight;
  const near = 0.1;
  const far = 1000;

  //Camera setup
  camera = new THREE.PerspectiveCamera(fov, aspect, near, far);
  camera.position.set(0, 90, 320);
  camera.lookAt(new THREE.Vector3(0,90,0));

  const axesHelper = new THREE.AxesHelper( 100 );
  //scene.add( axesHelper );

  //Renderer
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  const ambient = new THREE.AmbientLight(0x404040, 3.2);
  scene.add(ambient);

  const light = new THREE.SpotLight(0xffffff, 0.6);
  light.position.set(0, 500, 500);
  scene.add(light);

  
  //Load Model
  let loader = new THREE.GLTFLoader();
  loader.load("../static/claudia/scene.gltf", function(gltf) {
    scene.add(gltf.scene);
    house = gltf.scene.children[0];
    animate();
  });
  
}

function animate() {
  requestAnimationFrame(animate);
  house.rotation.z -= 0.01;
  renderer.render(scene, camera);
}


init();

function onWindowResize() {
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(container.clientWidth, container.clientHeight);
}

window.addEventListener("resize", onWindowResize);
