#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <signal.h>
#include <unistd.h>

typedef struct _PCB{
	int time_allotment;
	int pid;
}PCB;

typedef struct RQ_Node{
    PCB* data;
    struct RQ_Node* next;
}node;

int S = 0;	
int PRIO = 2;	// Highest Priority
int TS;
node* READY_QUEUE[3]={NULL,NULL,NULL};//ready queues
node* RUNNING = NULL;


void Insert_Node(node** head,node* n_node);
node* Delete_Node(node** head);
void schedule_handler(int signo);
void Put_Highest();

int main(int argc,char* argv[]){

	// Execptions	
	if(argc != 3){
		printf("ku_mlfq: Wrong number of arguments\n");
		exit(1);
	}
	int n = atoi(argv[1]);
	TS = atoi(argv[2]);
	if(n < 1 || n > 26){
		printf("ku_mlfq: Invalid argument value\n");
		exit(1);
	}
	
	// fork processes
	for(int i=0; i<n;i++){

		int child_pid;
		if ((child_pid=fork())==0){
			char arg[2] = {'A','\0'};
			arg[0] += i;
			execl("./ku_app","ku_app",arg,(char*)0);
		}
		else{
			// make PCB
			PCB* block = malloc(sizeof(PCB));
			block->time_allotment = 0;
			block->pid = child_pid;		
			
			//make node
			node* n_node =malloc(sizeof(node));
			n_node->data = block;
			n_node->next = NULL;
		
			// add at ready_Queue[2](highest priority queue)
			Insert_Node(&READY_QUEUE[2], n_node);
		}
	
	}

	// wait for execl
	sleep(5);
	
	// set signal handler
	signal(SIGALRM, schedule_handler);	
	
	// set timer
	struct itimerval delay;

	delay.it_value.tv_sec=1;
	delay.it_value.tv_usec=0;
	delay.it_interval.tv_sec=1;
        delay.it_interval.tv_usec=0;


	setitimer(ITIMER_REAL, &delay,NULL);
	
	while(1){
	
	}
	return 0;
}


//head : ready queue head, n_node : new node
void Insert_Node(node** head,node* n_node){

	if (*head==NULL){
		*head = n_node;
		return;
	}
	
	// find the end point
	node* c_node = *head;
	while(c_node->next !=NULL)
		c_node = c_node->next;
	
	// add
	c_node->next = n_node;

	return;

}

node* Delete_Node(node** head){
	
	if(*head ==NULL)
		return NULL;

	node* temp = *head;
	*head = (*head)->next;
	temp->next = NULL;

	return temp;
}

void Put_Highest(){ // put every nodes in the  highest queue

	while(1){
		node* temp = Delete_Node(&READY_QUEUE[1]);
		if (temp == NULL)
			break;
		else{
			temp->data->time_allotment = 0;
			Insert_Node(&READY_QUEUE[2], temp);
		}
	}
	while(1){
		node* temp = Delete_Node(&READY_QUEUE[0]);
		if (temp == NULL)
			break;
		else{
			temp->data->time_allotment = 0;
			Insert_Node(&READY_QUEUE[2], temp);
		}
	}
}

	
void schedule_handler(int signo){
	
	// first call
	if (RUNNING == NULL){
		kill(READY_QUEUE[PRIO]->data->pid,SIGCONT);
	        RUNNING = READY_QUEUE[PRIO];
		RUNNING->data->time_allotment += 1;
		return;
	}
	S++;	
	if (S == 10){
		S = 0;
		if(PRIO == 2 && RUNNING->data->time_allotment == 2){
			RUNNING->data->time_allotment = 0;
			Put_Highest();
			Insert_Node(&READY_QUEUE[1],Delete_Node(&READY_QUEUE[2]));
		}
  		else{
			// put running node at the end of the list
                        Insert_Node(&READY_QUEUE[PRIO],Delete_Node(&READY_QUEUE[PRIO]));
			Put_Highest();
			PRIO = 2; 
		}
	}
	else if(PRIO != 0){
		if (RUNNING->data->time_allotment != 2){
			// if allotment is become 1 -> move it to the last of the linked list.
			Insert_Node(&READY_QUEUE[PRIO],Delete_Node(&READY_QUEUE[PRIO]));
		}
		else{ 
			// if allotment become 2 -> move to lower level
			RUNNING->data->time_allotment = 0; 
	                Insert_Node(&READY_QUEUE[PRIO-1],Delete_Node(&READY_QUEUE[PRIO]));
			
			// if Running node was the only node in rq
			if(READY_QUEUE[PRIO] == NULL)
				PRIO--;
		}
	}
	else	// if S != 10 and PRIO == 0, changing allotment may be meaningless
		Insert_Node(&READY_QUEUE[PRIO],Delete_Node(&READY_QUEUE[PRIO]));

	TS--;	
	// when the program ends
	if (TS == 0)
	{
		// free allocated memory and kill children processes
		for (int i = 0; i<3;i++){
			while(1){
			       	node* temp = Delete_Node(&READY_QUEUE[i]);
				if (temp == NULL)
					break;
				else{
					// kill and reap
					kill(temp->data->pid,SIGKILL);
					waitpid(temp->data->pid,NULL,0);

					//free allocated memories
					free(temp->data);
					free(temp);
				}
			}
		}
                exit(0);
	}
	else{
		// context switching
		kill(RUNNING->data->pid,SIGSTOP);
		kill(READY_QUEUE[PRIO]->data->pid,SIGCONT);
		RUNNING = READY_QUEUE[PRIO];
		RUNNING->data->time_allotment += 1;
	}
	return;
}
