---
runme:
  id: 01HJQ7F9RYFAQG4NCAYG2PW00T
  version: v2.0
---

# aia-device

Natural Languague Understanding

```console {"id":"01HJQ7F9RXZBJJ4YEQA7Q49GYF"}
poetry run daemon

git ls-remote --get-url origin 
git remote set-url origin git@github_ranmadxs:ranmadxs/aia-device.git
```

## Docker

```sh {"id":"01HJV2GKHFHRCW2MAYBX6DWF7V"}
#set var entorno
export AIA_TAG_NLU=aia-device_0.1.0
```

```sh {"id":"01HJQ7F9RXZBJJ4YEQAAH1BXHZ"}
#build
docker build . --platform linux/arm64/v8 -t keitarodxs/aia:$AIA_TAG_NLU

#push
docker push keitarodxs/aia:$AIA_TAG_NLU

#go into docker container
sudo docker exec -ti aia_device bash

#run
docker run -d --rm -e TZ=America/Santiago -v /home/ranmadxs/aia/aia-cortex-nlu/target:/app/target --net=bridge --name aia_device --env-file .env keitarodxs/aia:$AIA_TAG_NLU
```

### Install Img

```sh {"id":"01HJQ7F9RXZBJJ4YEQAAX4XA1Y"}
docker save -o aia-cortex-nlu_$AIA_VERSION.tar keitarodxs/aia:$AIA_TAG_NLU

docker pull keitarodxs/aia:$AIA_TAG_NLU

docker load -i aia-device_$AIA_VERSION.tar
```
