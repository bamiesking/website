ZoomMtg.setZoomJSLib('https://source.zoom.us/1.7.9/lib', '/av'); 
ZoomMtg.preLoadWasm();
ZoomMtg.prepareJssdk();

ZoomMtg.init({
  debug: true,
  leaveUrl: meetConfig.leaveUrl,
  isSupportAV: true,
  success() {
    ZoomMtg.join({
      meetingNumber: meetConfig.meetingNumber,
      userName: meetConfig.userName,
      signature: signature,
      apiKey: meetConfig.apiKey,
      userEmail: meetConfig.userEmail,
      passWord: meetConfig.passWord,
      success() {
        resolve();
      },
      error(res) {
        console.log(res);
      }
    });
  },
  error(res) {
    console.log(res);
  }
});