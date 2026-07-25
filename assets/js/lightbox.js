import PhotoSwipeLightbox from "./photoswipe/photoswipe-lightbox.esm.js";
import PhotoSwipe from "./photoswipe/photoswipe.esm.js";
import PhotoSwipeDynamicCaption from "./photoswipe/photoswipe-dynamic-caption-plugin.esm.min.js";
import * as params from "@params";

const gallery = document.getElementById("gallery");

if (gallery) {
  const lightbox = new PhotoSwipeLightbox({
    gallery,
    children: ".gallery-item",
    showHideAnimationType: "zoom",
    bgOpacity: 1,
    pswpModule: PhotoSwipe,
    imageClickAction: "close",
    closeTitle: params.closeTitle,
    zoomTitle: params.zoomTitle,
    arrowPrevTitle: params.arrowPrevTitle,
    arrowNextTitle: params.arrowNextTitle,
    errorMsg: params.errorMsg,
  });

  if (params.enableDownload) {
    lightbox.on("uiRegister", () => {
      lightbox.pswp.ui.registerElement({
        name: "download-button",
        order: 8,
        isButton: true,
        tagName: "a",
        html: {
          isCustomSVG: true,
          inner: '<path d="M20.5 14.3 17.1 18V10h-2.2v7.9l-3.4-3.6L10 16l6 6.1 6-6.1ZM23 23H9v2h14Z" id="pswp__icn-download"/>',
          outlineID: "pswp__icn-download",
        },
        onInit: (el, pswp) => {
          el.setAttribute("download", "");
          el.setAttribute("target", "_blank");
          el.setAttribute("rel", "noopener");
          el.setAttribute("title", params.downloadTitle || "Download");
          pswp.on("change", () => {
            el.href = pswp.currSlide.data.element.href;
          });
        },
      });
    });
  }

  lightbox.on("change", () => {
    const target = lightbox.pswp.currSlide?.data?.element?.dataset["pswpTarget"];
    history.replaceState("", document.title, "#" + target);
  });

  lightbox.on("close", () => {
    history.replaceState("", document.title, window.location.pathname);
  });

  // --- Video slide support -------------------------------------------------
  // Anchors with data-pswp-type="video" get itemData.type === "video".
  // These handlers render an actual <video> element instead of an <img>,
  // reusing PhotoSwipe's own slide container, arrows and close behaviour.

  lightbox.on("contentLoad", (e) => {
    const { content } = e;
    if (content.type !== "video") return;
    e.preventDefault();

    const wrapper = document.createElement("div");
    wrapper.className = "pswp-video-wrapper";
    wrapper.style.cssText =
      "width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#000;";

    const video = document.createElement("video");
    video.setAttribute("controls", "");
    video.setAttribute("playsinline", "");
    video.style.cssText = "max-width:100%;max-height:100%;";

    const source = document.createElement("source");
    source.src = content.data.src;
    video.appendChild(source);
    wrapper.appendChild(video);

    content.element = wrapper;
    content.videoElement = video;
    content.onLoaded();
  });

  lightbox.on("contentResize", (e) => {
    const { content, width, height } = e;
    if (content.type !== "video") return;
    e.preventDefault();
    content.element.style.width = width + "px";
    content.element.style.height = height + "px";
  });

  lightbox.on("contentAppend", (e) => {
    const { content } = e;
    if (content.type !== "video") return;
    e.preventDefault();
    if (!content.element.parentNode) {
      content.slide.container.appendChild(content.element);
    }
  });

  lightbox.on("contentActivate", (e) => {
    const { content } = e;
    if (content.type !== "video" || !content.videoElement) return;
    content.videoElement.play().catch(() => {});
  });

  lightbox.on("contentDeactivate", (e) => {
    const { content } = e;
    if (content.type !== "video" || !content.videoElement) return;
    content.videoElement.pause();
  });

  lightbox.on("contentDestroy", (e) => {
    const { content } = e;
    if (content.type !== "video" || !content.videoElement) return;
    content.videoElement.pause();
    content.videoElement.removeAttribute("src");
    content.videoElement.load();
  });
  // --------------------------------------------------------------------------

  new PhotoSwipeDynamicCaption(lightbox, {
    mobileLayoutBreakpoint: 700,
    type: "auto",
    mobileCaptionOverlapRatio: 1,
  });

  lightbox.init();

  if (window.location.hash.substring(1).length > 1) {
    const target = window.location.hash.substring(1);
    const items = gallery.querySelectorAll("a");
    for (let i = 0; i < items.length; i++) {
      if (items[i].dataset["pswpTarget"] === target) {
        lightbox.loadAndOpen(i, { gallery });
        break;
      }
    }
  }
}