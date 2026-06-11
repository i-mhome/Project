import easyocr #ocr - 사진을 읽는 모듈을 가져옴
#OCR 광학문자인식 - 텍스트 데이터로 치환한다.
import csv #csv 파일을 다루기 위한 파이썬 기본 모듈을 가져 온다
import os #폴더 안 파일 목록을 읽을 때 쓰는 기본 모듈


def main():#메인 함수
    while True:
        print('\n===== 로보 자비스 정산 프로그램 =====')
        print('1. 직접 입력으로 정산하기')
        print('2. OCR 이미지로 정산하기')
        print('3. 종료')

        choice = input('메뉴를 선택하세요: ')

        if choice == '1':
            run_manual_settlement()
        
        elif choice == '2':
            run_ocr_settlement()
        
        elif choice == '3':
            print('프로그램을 종료합니다.')
            break

        else:
            print('잘못된 메뉴입니다. 다시 선택하세요.')


def run_manual_settlement(): #직접 입력 방식으로 정산을 실행하는 함수
    print('\n===== 직접 입력 정산 =====')

    all_members_input = input("전체 명단을 입력하세요. 예) 김철수, 이영희, 박민수: ")
    paid_members_input = input("체크된 사람 명단을 입력하세요. 예) 김철수, 이영희: ")
    while True:
        #올바른 숫자 금액이 입력될 때까지 반복한다.
        try:
            total_amount = int(input('행사 총 금액을 입력하세요: '))
            break
        except ValueError: 
            print('숫자만 입력해주세요. 예) 80000')
            #숫자가 아닌 값을 입력하면 int변환에서 ValueError가 발생한다.

    all_members = split_names(all_members_input)
    #전체 명단 문자열을 리스트로 변환
    paid_members = split_names(paid_members_input)
    #입금자 명단 문자열을 리스트로 변환

    process_settlement(all_members, paid_members, total_amount)
    #변환된 명단과 총 금액을 이용해 정산 진행


def run_ocr_settlement(): #OCR 이미지 정산 담당
    print("\n===== OCR 이미지 정산 =====")

    all_folder_path = input("참여 명단 이미지 폴더명을 입력하세요. 예) all_images: ")
    #전체 참여 명단 이미지들이 들어 있는 폴더명을 입력받는다.
    paid_folder_path = input("체크 명단 이미지 폴더명을 입력하세요. 예) paid_images: ")

    all_image_paths = get_image_paths_from_folder(all_folder_path)
    #참여 명단 폴더 안에 있는 이미지 파일 경로들을 가져온다. 이미 만들어놓은 함수로 진행
    paid_image_paths = get_image_paths_from_folder(paid_folder_path)
    #체크 명단도 동일하게 진행

    if len(all_image_paths) == 0:
        print("참여 명단 이미지가 없습니다.")
        return

    if len(paid_image_paths) == 0:
        print("체크 명단 이미지가 없습니다.")
        return

    print("\n[참여 명단 이미지 파일]")
    print(all_image_paths)#어떤 참여 명단 이미지 파일을 읽을지 출력

    print("\n[체크 명단 이미지 파일]")
    print(paid_image_paths)#실제로 어떤 체크 명단 이미지 파일을 읽을지 출력

    all_members = read_names_from_images(all_image_paths)
    #참여 명단 이미지들을 OCR로 읽어 전체 명단 리스트를 만든다.
    paid_members = read_names_from_images(paid_image_paths)
    #체크 명단 이미지도 OCR로 읽어 체크 명단 리스트를 만든다.

    print("\n===== OCR로 읽은 참여 명단 =====")
    print(all_members)
    #OCR로 읽은 전체 참여 명단 출력

    print("\n===== OCR로 읽은 체크 명단 =====")
    print(paid_members)

    while True:
        #위에 있는 오류 TRY EXCEPT와 동일
        try:
            total_amount = int(input("행사 총 금액을 입력하세요: "))
            break
        except ValueError:
            print("숫자만 입력해주세요. 예) 80000")

    process_settlement(all_members, paid_members, total_amount)
    #OCR로 얻은 명단과 총 금액을 이용해 정산을 진행


def split_names(text): #입력 문자열을 이름 리스트로 변환
    return [name.strip() for name in text.split(",") if name.strip()]
    #사용자가 쉼표로 입력한 문자열을 이름 리스트로 바꾼다
    #text.split(",") : 쉼표를 기준으로 문자열을 나눈다.
    #name.strip() : 이름 앞뒤의 공백을 제거
    #if name.strip() : 빈 문자열은 리스트에 넣지 않는다.


def get_image_paths_from_folder(folder_path):
    image_paths = [] #이미지 파일 경로 저장할 빈 리스트

    for file_name in os.listdir(folder_path): #해당 폴더 안에 있는 파일 이름들을 전부 가져옴
        if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
            #.lower()는 파일 이름을 소문자로 바꿈, endswith - 저런 사진 파일로 끝나는지
            image_path = os.path.join(folder_path, file_name) #폴더명과 파일명 합쳐서 실제 경로로 만든다.
            image_paths.append(image_path) #경로를 image_paths에 추가

    return image_paths


def read_names_from_images(image_paths): #이미지 여러장을 하나씩 OCR로 읽고 읽은 이름들을 합쳐 중복 이름 제거
    all_names = []
    #중복된 이름은 한번만 저장

    for image_path in image_paths: #이미지 경로를 하나씩 가져온다
        text = read_text_from_image(image_path)
        #이미지 한 장에서 OCR로 텍스트를 읽는다.
        names = text_to_names(text)
        #OCR로 읽은 텍스트를 이름 리스트로 바꾼다.

        for name in names:#현재 이미지에서 읽은 이름들을 하나씩 확인
            if name not in all_names:#이미 저장된 이름이 아니면
                all_names.append(name)
                #전체 이름 리스트에 추가한다.

    return all_names


def read_text_from_image(image_path):#이미지 한 장에서 글자를 읽어 문자열로 반환하는 함수
    reader = easyocr.Reader(['ko', 'en'],gpu = True)
    #EasyOCR Reader 객체를 만들고, 한글과 영어를 인식하겠다는 뜻
    results = reader.readtext(image_path, detail=0)
    #이미지에서 글자를 읽는데, detail = 0이라는 뜻은 글자의 위치정보 없이 텍스트만 가져오겠다는것

    text = "\n".join(results)
    #OCR 결과 리스트를 줄바꿈이 포함된 하나의 문자열로 합친다.
    return text
    

def text_to_names(text): #OCR로 읽은 문자열을 이름 리스트로 변환하는 함수
    names = []
    # 이름들을 저장할 빈 리스트

    for line in text.splitlines():
        #OCR 결과 문자열을 줄 단위로 나누어 한 줄씩 확인한다.
        name = line.strip() #줄 앞뒤 공백을 제거한다.
        name = name.replace(" ", "") 
        #이름 중간에 들어간 공백을 제거한다.
    
        if name: #name이 빈 문자열이 아니라면
            names.append(name)
            #이름 리스트에 추가한다.

    return names    


def process_settlement(all_members, paid_members, total_amount): #계산, 출력, 저장을 묶어서 처리
    if len(all_members) == 0:
        print('전체 명단이 비어 있습니다.')
        return
    #전체 명단이 없으면 계산이 불가능하므로 중단

    unpaid_people, unknown_people, per_person_amount = calculate_settlement(
        all_members,
        paid_members,
        total_amount
    ) # calculate_settlement 함수에서 정산 계산 결과 3개를 받아온다.

    print_settlement_result(
        all_members,
        paid_members,
        unpaid_people,
        unknown_people,
        per_person_amount
    ) #계산된 정산 결과를 화면에 출력합니다.
    
    save_result_to_csv(all_members, paid_members, unpaid_people, per_person_amount)
    print('정산 결과가 settlement_result.csv 파일로 저장되었습니다.')
    #정산 결과를 csv파일로 저장합니다.


def calculate_settlement(all_members, paid_members, total_amount): #정산 계산 담당
    unpaid_people = find_unpaid_people(all_members, paid_members) #미입금자 명단 계산
    unknown_people = find_unknown_people(all_members, paid_members)#명단에 없는 체크이름 계산
    per_person_amount = total_amount // len(all_members) #1인당 금액 계산, // 정수 나눗셈 소수 밑 버림

    return unpaid_people, unknown_people, per_person_amount
#이 함수를 만든 이유는 run_manual_settlement가 너무 많은 일을 하고 있다.
#계산 부분만 따로 빼서 이 함수가 담당하도록 만들었다.


def find_unpaid_people(all_members, paid_members): #미 입금자 찾기 담당
    unpaid = [] #미 입금자를 저장할 빈 리스트

    for member in all_members: #전체 명단 한명씩 확인
        if member not in paid_members:
            unpaid.append(member)

    return unpaid


def find_unknown_people(all_members, paid_members): #전체 명단에 없는 이름 찾기 담당
    unknown = [] #전체 명단에 없는 이름을 저장할 빈 리스트

    for person in paid_members :
        if person not in all_members:
            unknown.append(person)
    
    return unknown


def print_settlement_result(all_members, paid_members, unpaid_people, unknown_people, per_person_amount):
    
    print("\n===== 정산 결과 =====")
    print("전체 인원:", all_members)
    print("체크된 사람:", paid_members)
    print("미입금자:", unpaid_people)
    print('전체 명단에 없는 체크 이름:', unknown_people)
    print("전체 인원 수:", len(all_members), "명")
    print("1인당 금액:", per_person_amount, "원")

    if len(unknown_people) > 0:
        print('\n[주의] 체크 명단에 전체 명단에 없는 이름이 있습니다.')
        #전체 명단에는 없는데 체크 명단에는 있는 이름이 하나라도 있으면 경고를 출력
        
        for person in unknown_people:
            print(f'- {person}')
            #문제가 되는 이름을 하나씩 출력

    if len(unpaid_people) == 0:
        print("모든 사람이 체크되었습니다.") #미 입금자가 없으면 전원이 체크 완료된 상태
    else:
        print(f"총 {len(unpaid_people)}명이 미입금 상태입니다.")

        for person in unpaid_people: #미입금자 한명씩 반복문을 돌려 출력함
            print(f'{person}님은 {per_person_amount}원을 내야 합니다.')
        #미 입금자별로 내야 할 금액을 출력한다.
#정산 결과 출력 담당


def save_result_to_csv(all_members, paid_members, unpaid_people, per_person_amount): 
    with open("settlement_result.csv", 'w', newline = '', encoding = 'utf-8-sig') as file: #settlement_result.csv라는 파일을 여는 코드
    #파이썬을 쓸때 파일을 열었으면 닫아야되는데(open, close함수 사용)
    #닫지 않으면 파일저장이 제대로 안되고 다른 프로그램에서 파일을 못 열 수도 있음
    #메모리 낭비가 생길 수 있음
    #with를 쓰면 close를 안써도 됨
    #with 블록이 끝나면 파이썬이 자동으로 파일을 닫아주기 때문
    #'w'는 쓰기모드, encoding은 엑셀에서 한글이 깨지지 않게 하기 위해 쓰는 설정
        writer = csv.writer(file)
        #csv파일에 한 줄 씩 쓰기 위한 writer 객체를 만드는 줄이다.

        writer.writerow(['이름', '상태', '납부금액'])
        #csv파일의 첫 줄, 즉 제목 줄을 쓰는 코드

        for member in all_members:
        #전체 명단을 한 명씩 확인하는 반복문
            if member in paid_members : #member가 명단에 있으면 체크가 완료된걸로 본다
                status = '체크완료'
            else :
                status = '미입금'
            
            writer.writerow([member, status, per_person_amount])
            #이름, 상태, 납부금액을 CSV파일에 한 줄로 저장한다(writerow:행에 저장한다)


main()